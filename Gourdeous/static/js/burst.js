! function () {
var width = 960,
    height = 700,
    radius = (Math.min(width, height) / 2) - 10;

var formatNumber = d3.format(",d");

var x = d3.scaleLinear()
    .range([0, 2 * Math.PI]);

var y = d3.scaleSqrt()
    .range([0, radius]);

var color = d3.scaleOrdinal(d3.schemeCategory20);

var partition = d3.partition();

var arc = d3.arc()
    .startAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x0))); })
    .endAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x1))); })
    .innerRadius(function(d) { return Math.max(0, y(d.y0)); })
    .outerRadius(function(d) { return Math.max(0, y(d.y1)); });

// Create the svg element
var svg = d3.select("#vis").append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", "translate(" + width / 2 + "," + (height / 2) + ")");

// Load the json file
d3.json("static/js/wheel.json", function(error, root) {
    if (error) throw error;
    root = d3.hierarchy(root);
    root.sum(function(d) { return d.size; });
    var path = svg.selectAll("path")
        .data(partition(root).descendants())
        .enter().append("g")
        .attr("nameofg","gname")
        path.append("path")
        .attr("d", arc)
            .attr("name","disname")
        .style("fill", function(d) { return color((d.children ? d : d.parent).data.name); })
        .on("click", click)
        .text(function(name) { alert("Q1"+ name+" "+name);return name.data.name + "\n" + formatNumber(name.value); });

    path.append("text")
        .text(function(name) { alert("Q"+ name+" "+name); return name})
        .classed("label", true)
        .attr("x", function(d) { return d.x; })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
            if (d.depth > 0) {
                return "translate(" + arc.centroid(d) + ")" +
                       "rotate(" + getAngle(d) + ")";
            }  else {
                return null;
            }
        })
        .attr("dx", "6") // margin
        .attr("dy", ".35em") // vertical-align
        .attr("pointer-events", "none");
});

// Handles the click
function click(d) {
  svg.transition()
      .duration(750)
      .tween("scale", function() {
        var xd = d3.interpolate(x.domain(), [d.x0, d.x1]),
            yd = d3.interpolate(y.domain(), [d.y0, 1]),
            yr = d3.interpolate(y.range(), [d.y0 ? 20 : 0, radius]);
        return function(t) { x.domain(xd(t)); y.domain(yd(t)).range(yr(t)); };
      })
      .selectAll("path")
      .attrTween("d", function(d) { return function() { return arc(d); }; });
}

d3.select(self.frameElement).style("height", height + "px");
}();

function getAngle(d) {
    alert("angle")
    // Offset the angle by 90 deg since the '0' degree axis for arc is Y axis, while
    // for text it is the X axis.
    var thetaDeg = (180 / Math.PI * (arc.startAngle()(d) + arc.endAngle()(d)) / 2 - 90);
    // If we are rotating the text by more than 90 deg, then "flip" it.
    // This is why "text-anchor", "middle" is important, otherwise, this "flip" would
    // a little harder.
    return (thetaDeg > 90) ? thetaDeg - 180 : thetaDeg;
}