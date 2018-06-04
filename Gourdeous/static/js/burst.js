! function () {
    var width = 960,
        height = 700,
        radius = (Math.min(width, height) / 2) - 10;

    var formatNumber = d3.format(",d");

    var x = d3.scaleLinear()
        .range([0, 2 * Math.PI]);

    var y = d3.scaleLinear()
        .range([0, radius]);

    var color = d3.scaleOrdinal(d3.schemeCategory20);

    var partition = d3.partition();

    var arc = d3.arc()
        .startAngle(function (d) {
            return Math.max(0, Math.min(2 * Math.PI, x(d.x0)));
        })
        .endAngle(function (d) {
            return Math.max(0, Math.min(2 * Math.PI, x(d.x1)));
        })
        .innerRadius(function (d) {
            return Math.max(0, y(d.y0));
        })
        .outerRadius(function (d) {
            return Math.max(0, y(d.y1));
        });

// Create the svg element
    var svg = d3.select("#vis").append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + width / 2 + "," + (height / 2) + ")");

// Load the json file
d3.json("static/js/wheel.json", function (error, root) {
    if (error) throw error;
    root = d3.hierarchy(root);
    root.sum(function(d) { return d.size; });

    var g = svg.selectAll("path")
        .data(partition(root).descendants())
        .enter().append("g");

    var path = g.append("path")
        .attr("d", arc)
        .style("fill", function(d) { return color((d.children ? d : d.parent).data.name); })
        .on("click", click);

    var text = g.append("text")
        .attr("transform", function(d) {
            if(d.depth > 0){
                return "translate(" + arc.centroid(d) + ")rotate(" + getAngle(d) + ")";
            }else {
                return null;
            }})
        .attr("text-anchor", "middle")
        .attr("dx", "6") // margin
        .attr("dy", ".35em") // vertical-align
        .style("font-size", "9px")
        .text(function(d) {return d.data.name})
        .attr("pointer-events", "none");


// Handles the click
function click(d) {
    text.transition().attr("opacity", 0);
    //transition.selectAll("text")
    path.transition()
        .duration(750)
        .tween("scale", function () {
            var xd = d3.interpolate(x.domain(), [d.x0, d.x1]),
                yd = d3.interpolate(y.domain(), [d.y0, 1]),
                yr = d3.interpolate(y.range(), [d.y0 ? 20 : 0, radius]);
            return function (t) {
                x.domain(xd(t));
                y.domain(yd(t)).range(yr(t));};})



        .attrTween("d", function (d) {
            return function () {return arc(d);};})
        .on("end", function (e, i) {
            if(e.x0 >= d.x0 && e.x0 < (d.x1)){
                var arcText = d3.select(this.parentNode).select("text");
                arcText.transition().duration(750)
                    .attr("opacity", 1)
                    .attr("transform", function(d){return "translate(" + arc.centroid(d) + ")rotate(" + getAngle(d) + ")";})
                    .attr("text-anchor", "middle")
                    .text(function(d){
                        return d.data.name == "root" ? "" : d.data.name});
        }})
}});
d3.select(self.frameElement).style("height", height + "px");


function getAngle(d) {
    // Offset the angle by 90 deg since the '0' degree axis for arc is Y axis, while
    // for text it is the X axis.
    var thetaDeg = (180 / Math.PI * (arc.startAngle()(d) + arc.endAngle()(d)) / 2 - 90);
    // If we are rotating the text by more than 90 deg, then "flip" it.
    // This is why "text-anchor", "middle" is important, otherwise, this "flip" would
    // a little harder.
    return (thetaDeg > 90) ? thetaDeg + 180 : thetaDeg;
}
}();