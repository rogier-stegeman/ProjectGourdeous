function jeSunnigeBoi(Jayson_derulo, rate_value1, rate_value2, rate_value3){
try{
        const width = window.innerWidth,
            height = window.innerHeight,
            maxRadius = (Math.min(width, height) / 2) - 5;

        const formatNumber = d3.format(',d');

        const x = d3.scaleLinear()
            .range([0, 2 * Math.PI])
            .clamp(true);

        const y = d3.scaleSqrt()
            .range([maxRadius*.1, maxRadius]);  //bepaald de open ruimte in ht midden

        const color = d3.scaleOrdinal(d3.schemeCategory20);

        const partition = d3.partition();

        const arc = d3.arc()
            .startAngle(d => x(d.x0))
            .endAngle(d => x(d.x1))
            .innerRadius(d => Math.max(0, y(d.y0)))
            .outerRadius(d => Math.max(0, y(d.y1)));

        const middleArcLine = d => {
            const halfPi = Math.PI/2;
            const angles = [x(d.x0) - halfPi, x(d.x1) - halfPi];
            const r = Math.max(0, (y(d.y0) + y(d.y1)) / 2);

            const middleAngle = (angles[1] + angles[0]) / 2;
            const invertDirection = middleAngle > 0 && middleAngle < Math.PI; // On lower quadrants write text ccw
            if (invertDirection) { angles.reverse(); }

            const path = d3.path();
            path.arc(0, 0, r, angles[0], angles[1], invertDirection);
            return path.toString();
        };

        const textFits = d => {
            const CHAR_SPACE = 6;

            const deltaAngle = x(d.x1) - x(d.x0);
            const r = Math.max(0, (y(d.y0) + y(d.y1)) / 2);
            const perimeter = r * deltaAngle;

            return d.data.name.length * CHAR_SPACE < perimeter;
        };

        const svg = d3.select('#sun').append('svg')
            .style('width', '100vw')                //postie
            .style('height', '100vh')
            .attr('viewBox', `${-width / 2} ${-height / 2} ${width} ${height}`)
            .on('click', () => focusOn()); // Reset zoom on canvas click
        
        //getData(Jayson_derulo, rate_value1, rate_value2, rate_value3);
        
        
        var url = "http://cytosine.nl/~owe8_pg2/testytest/htmltesttt/Bittericious2/index.wsgi/_sun_data?a="+rate_value1+"&b="+rate_value2+"&c="+rate_value3
        d3.json(url, (error, root) => {
            if (error) throw error;
            
            //var data = getData(rate_value1, rate_value2, rate_value3)
            //document.getElementById("r4").innerHTML = data;
            //root = d3.hierarchy(data);
            root = d3.hierarchy(root);
            root.sum(d => d.size);

            const slice = svg.selectAll('g.slice')
                .data(partition(root).descendants());

            slice.exit().remove();

            const newSlice = slice.enter()
                .append('g').attr('class', 'slice')
                .on('click', d => {
                    d3.event.stopPropagation();
                    focusOn(d);
                    setText(d);
                });

            newSlice.append('title')
                .text(d => d.data.name + '\n' + formatNumber(d.value));

            newSlice.append('path')
                .attr('class', 'main-arc')
                .style('fill', d => color((d.children ? d : d.parent).data.name))
                .attr('d', arc);

            newSlice.append('path')
                .attr('class', 'hidden-arc')
                .attr('id', (_, i) => `hiddenArc${i}`)
                .attr('d', middleArcLine);

            const text = newSlice.append('text')
                .attr('display', d => textFits(d) ? null : 'none');

            // Add white contour
            text.append('textPath')
                .attr('startOffset','50%')
                .attr('xlink:href', (_, i) => `#hiddenArc${i}` )
                .text(d => d.data.name)
                .style('fill', 'none')
                .style('stroke', '#fff')
                .style('stroke-width', 5)
                .style('stroke-linejoin', 'round');

            text.append('textPath')
                .attr('startOffset','50%')
                .attr('xlink:href', (_, i) => `#hiddenArc${i}` )
                .text(d => d.data.name);
        });

        function focusOn(d = { x0: 0, x1: 1, y0: 0, y1: 1 }) {
            // Reset to top-level if no data point specified

            const transition = svg.transition()
                .duration(750)  	           // snelheid boissss
                .tween('scale', () => {
                    const xd = d3.interpolate(x.domain(), [d.x0, d.x1]),
                        yd = d3.interpolate(y.domain(), [d.y0, 1]);
                    return t => { x.domain(xd(t)); y.domain(yd(t)); };
                });

            transition.selectAll('path.main-arc')
                .attrTween('d', d => () => arc(d));

            transition.selectAll('path.hidden-arc')
                .attrTween('d', d => () => middleArcLine(d));

            transition.selectAll('text')
                .attrTween('display', d => () => textFits(d) ? null : 'none');
            
            moveStackToFront(d);

            //

            function moveStackToFront(elD) {
                svg.selectAll('.slice').filter(d => d === elD)
                    .each(function(d) {
                        this.parentNode.appendChild(this);
                        if (d.parent) { moveStackToFront(d.parent); }
                    })
            }
        }
                
        function setText2(d){
            document.getElementById("suntable").innerHTML = "adsfdsafsda";
            $.getJSON($SCRIPT_ROOT + '/_info_data',
                        {a: d.data.name}, 
                        function(data) {
                                console.log("I want to die");
                                document.getElementById("suntable").innerHTML = "succesfol gekozen voor leerrichting";
                                document.getElementById("suntable").innerHTML = data;
                              });
                              
                              return false;
                          
                          
        }
        
        function setText(d){
        
			var rate_value1 = 1;
			var rate_value2 = 2;
			var rate_value3 = 3;
						
			if (document.getElementById('tabChoice1').checked) {
              rate_value1 = document.getElementById('tabChoice1').value;
                }
          else if(document.getElementById('tabChoice2').checked) {
                  rate_value1 = document.getElementById('tabChoice2').value;
                }
          else if(document.getElementById('tabChoice3').checked) {
                  rate_value1 = document.getElementById('tabChoice3').value;
                }
           if (document.getElementById('tabChoice4').checked) {
                  rate_value2 = document.getElementById('tabChoice4').value;
                }
            else if(document.getElementById('tabChoice5').checked) {
                  rate_value2 = document.getElementById('tabChoice5').value;
                }
            else if(document.getElementById('tabChoice6').checked) {
                  rate_value2 = document.getElementById('tabChoice6').value;
                }
            if(document.getElementById('tabChoice7').checked) {
                  rate_value3 = document.getElementById('tabChoice7').value;
                }
            else if(document.getElementById('tabChoice8').checked) {
                  rate_value3 = document.getElementById('tabChoice8').value;
                }
            else if(document.getElementById('tabChoice9').checked) {
                  rate_value3 = document.getElementById('tabChoice9').value;
                }
        

            var earl = $SCRIPT_ROOT + '/_info_data' + "?a=" + d.data.name 
            var xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
            document.getElementById("suntable").innerHTML = this.responseText;
            yeet()
            }
          };
          xhttp.open("GET", earl, true);
          xhttp.send();
        
        
        }
        
    } catch(err) {
                document.getElementById("r4").innerHTML = err.message;
            }
}

