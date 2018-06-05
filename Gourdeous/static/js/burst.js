/*
    This javascript is responsible for creating the sunburst visualisation using the d3 library.
    The sunburst is then placed in the html in the tag <svg> which this script also creates.

    Authors: Rogier and Awan

    Known bugs: Can't extract articles from the json file yet.
 */

//This function is called by the sunburst.html and contains all the code in this file since it has to run it all.
! function () {
var width = 700,
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
d3.json("static/js/Jason.json", function(error, root) {
    if (error) throw error;
    root = d3.hierarchy(root);
    root.sum(function(d) { return d.size; });

    var path = svg.selectAll("path")
        .data(partition(root).descendants())
        .enter().append("g");
        path.append("path")
        .attr("d", arc)
            .attr("name",function (name) {return name.data.name})
            .attr("articles", function (name) {return name.data.articles})
        .style("fill", function(d) { return color((d.children ? d : d.parent).data.name); })
            .on("click", showArticles)
        .on("dblclick", zoom)
            .on("mouseover", highlight)
            .on("mouseout",function () {
                d3.selectAll("path").style("fill", function(d) { return color((d.children ? d : d.parent).data.name); })
                    .style("stroke", "#000")
                    .style("stroke-width","1")
            })
        .append("title",function(name) {return name.data.name + "\n" + formatNumber(name.value)})
        .text(function(name) { /*alert("Q1"+ name+" "+name)*/;return name.data.name + "\n" + formatNumber(name.value)
            //.append("name",function (name) {return name.data.name})
            //.text(function (name) {return name.data.name})
        ;})


    /*object object
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
    */
});

function showArticles() {
    var searchName = d3.select(this).attr("name");
    var articleArray = d3.select(this).attr("articles");
    //alert(searchName+" - "+articleArray);
    var articles = articleArray.split(",");
    var tableArray = [];
    var index = 0;
    for (var i1=0,i2=1,  tot=articles.length; i1 < tot; i1+=3,i2+=3) {
        //var link = "<a href='"+articles[i2]+"'>"+articles[i1]+"</a>";
        tableArray.push([[articles[i1],articles[i2]]]);
    }
    for (var i2=1, i1=3, i3=0, tot=articles.length; i2 < tot; i2+=3,i3++, i1+=3) {
        index = i1 - 1;
        tableArray[i3].push(articles[index]);
    }
    console.log(tableArray);
    //alert(tableArray);
    //var testA = [["titel1","www.pubmed.gov/racecar_methanol_study",1000],["tital2","www.pubmed.gov/beer_destroys_fat_levels",500],["titel3","www.pubmed.gov/Bittergourd_tea_recipes",3021]];
    createTable(tableArray);
}


function createTable(tableData) {
    var table = document.createElement('table');
    var tableBody = document.createElement('tbody');

    tableData.forEach(function(rowData) {
        var row = document.createElement('tr');
        rowData.forEach(function(cellData) {
        var cell = document.createElement('td');
        console.log("cell: "+cellData);
        if (cellData.includes("www.")){
            cell.appendChild(document.createTextNode(""));
        } else {
            cell.appendChild(document.createTextNode(cellData));
        }
        row.appendChild(cell);

    });

    tableBody.appendChild(row);
  });

  table.appendChild(tableBody);
  document.getElementById("article-field").appendChild(table);
    //alert(table);
    console.log(table);
    return table;
}


// This function is called when a user double clicks on a node. It will make this node the new center of the sunburst
// by zooming in on it and adjusting the other nodes.
function zoom(d) {
  svg.transition()
      .duration(700)
      .tween("scale", function() {
        var xd = d3.interpolate(x.domain(), [d.x0, d.x1]),
            yd = d3.interpolate(y.domain(), [d.y0, 1]),
            yr = d3.interpolate(y.range(), [d.y0 ? 20 : 0, radius]);
        return function(t) { x.domain(xd(t)); y.domain(yd(t)).range(yr(t)); };
      })
      .selectAll("path")
      .attrTween("d", function(d) { return function() { return arc(d); }; });
}

// This function is called when the user hovers the mouse over a node.
// It will highlight this node and all other nodes with the same name.
function highlight() {
    var name = d3.select(this).attr("name");
    var col = d3.select(this).style("fill");
    d3.selectAll("path")
        .filter(function (d) {
        return d3.select(this).attr("name") === name;
        })
        .style('fill', 'orange')
        .style('stroke','#ff0d3c')
        .style("stroke-width","3");
}

d3.select(self.frameElement).style("height", height + "px");
}();

// [From template]
// Used to rotate the sunburst text.
function getAngle(d) {
    alert("angle");
    // Offset the angle by 90 deg since the '0' degree axis for arc is Y axis, while
    // for text it is the X axis.
    var thetaDeg = (180 / Math.PI * (arc.startAngle()(d) + arc.endAngle()(d)) / 2 - 90);
    // If we are rotating the text by more than 90 deg, then "flip" it.
    // This is why "text-anchor", "middle" is important, otherwise, this "flip" would
    // a little harder.
    return (thetaDeg > 90) ? thetaDeg - 180 : thetaDeg;
}
/*
d3.select("#highlightClear").on("click",function () {
    var color = d3.scaleOrdinal(d3.schemeCategory20);
    d3.selectAll("path")
        .data(partition(root).descendants())
        .enter()
            .style("fill", function(d) { return color((d.children ? d : d.parent).data.name); })
              .style("stroke", "#000")
              .style("stroke-width", "1");
});
*/

d3.select("#highlightWord").on("input", function() {
    var name = this.value;
    d3.selectAll("path")
        .filter(function (d) {
        return d3.select(this).attr("name") === name;
        })
        .style('fill', 'orange')
        .style('stroke','#ff0d3c')
        .style("stroke-width","3");
});


/*
function showArticles() {
    var searchName = d3.select(this).attr("name");
    var articleArray = d3.select(this).attr("articles");
    alert(searchName+" - "+articleArray);
    var articles = articleArray.split(",");
    var tableArray = [];
    var index = 0;
    for (var i1=0,  tot=articles.length; i1 < tot; i1+=3) {
        tableArray.push([articles[i1]]);
    }
    for (var i2=1, i1=2, i3=0, tot=articles.length; i2 < tot; i2+=2,i3++, i1+=2) {
        index = i1 - 1;
        tableArray[i3].push(articles[index]);
    }
    console.log(tableArray);
    alert(tableArray);
    var testA = [["www.pubmed.gov/racecar_methanol_study",1000],["www.pubmed.gov/beer_destroys_fat_levels",500],["www.pubmed.gov/Bittergourd_tea_recipes",3021]];
    createTable(testA);
}
*/

