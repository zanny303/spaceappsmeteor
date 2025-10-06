// src/components/ImpactMap.js
import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const ImpactMap = ({ missionPlan, safeTrajectory }) => {
  const svgRef = useRef(null);

  useEffect(() => {
    if (!missionPlan || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous

    const width = 600;
    const height = 400;
    const margin = { top: 20, right: 20, bottom: 30, left: 40 };

    svg.attr('width', width).attr('height', height);

    // Create projection
    const projection = d3.geoNaturalEarth1()
      .scale(150)
      .translate([width / 2, height / 2]);

    // Draw base map
    const land = svg.append('path')
      .datum({type: "Sphere"})
      .attr("d", d3.geoPath(projection))
      .attr("fill", "#1e3a5f")
      .attr("stroke", "#2d4d7a");

    // Add graticule (grid lines)
    const graticule = d3.geoGraticule();
    svg.append("path")
      .datum(graticule)
      .attr("d", d3.geoPath(projection))
      .attr("fill", "none")
      .attr("stroke", "#3a5f8a")
      .attr("stroke-width", 0.5)
      .attr("stroke-opacity", 0.3);

    // Plot impact risk zones
    const consequences = missionPlan.ai_predicted_consequences;
    if (consequences) {
      // Use a realistic impact point (could be enhanced with actual trajectory intersection)
      const impactPoint = [0, 20]; // Prime meridian, 20°N for demo
      const projectedPoint = projection(impactPoint);

      // Blast zone
      if (consequences.blast_radius_km > 0) {
        const blastRadius = Math.min(consequences.blast_radius_km / 50, 80); // Scale for visualization
        const blastCircle = d3.geoCircle()
          .center(impactPoint)
          .radius(blastRadius);

        svg.append('path')
          .datum(blastCircle())
          .attr('d', d3.geoPath(projection))
          .attr('fill', '#ff4444')
          .attr('opacity', 0.4)
          .attr('stroke', '#ff0000')
          .attr('stroke-width', 1.5);
      }

      // Tsunami zone (if significant)
      if (consequences.inundation_radius_km > 50) {
        const tsunamiRadius = Math.min(consequences.inundation_radius_km / 30, 120);
        const tsunamiCircle = d3.geoCircle()
          .center(impactPoint)
          .radius(tsunamiRadius);

        svg.append('path')
          .datum(tsunamiCircle())
          .attr('d', d3.geoPath(projection))
          .attr('fill', '#4444ff')
          .attr('opacity', 0.3)
          .attr('stroke', '#0000ff')
          .attr('stroke-width', 1);
      }

      // Seismic effect zone
      if (consequences.predicted_seismic_magnitude > 6) {
        const seismicRadius = consequences.predicted_seismic_magnitude * 8;
        const seismicCircle = d3.geoCircle()
          .center(impactPoint)
          .radius(seismicRadius);

        svg.append('path')
          .datum(seismicCircle())
          .attr('d', d3.geoPath(projection))
          .attr('fill', 'none')
          .attr('stroke', '#ffaa00')
          .attr('stroke-width', 1)
          .attr('stroke-dasharray', '5,5');
      }

      // Impact epicenter
      svg.append('circle')
        .attr('cx', projectedPoint[0])
        .attr('cy', projectedPoint[1])
        .attr('r', 6)
        .attr('fill', '#ff0000')
        .attr('stroke', '#ffffff')
        .attr('stroke-width', 2);

      // Add impact point label
      svg.append('text')
        .attr('x', projectedPoint[0] + 10)
        .attr('y', projectedPoint[1] - 10)
        .text('Impact Epicenter')
        .attr('fill', '#ff4444')
        .attr('font-size', '10px')
        .attr('font-weight', 'bold');
    }

    // Add legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 160}, ${height - 120})`);

    // Legend background
    legend.append('rect')
      .attr('width', 150)
      .attr('height', consequences ? 100 : 40)
      .attr('fill', 'rgba(0, 0, 0, 0.7)')
      .attr('stroke', '#444')
      .attr('rx', 5);

    legend.append('text')
      .attr('x', 75)
      .attr('y', 15)
      .text('Impact Zones Legend')
      .attr('fill', '#fff')
      .attr('font-size', '10px')
      .attr('font-weight', 'bold')
      .attr('text-anchor', 'middle');

    if (consequences) {
      const legendItems = [
        { color: '#ff4444', text: `Blast Radius: ${consequences.blast_radius_km}km` },
        { color: '#4444ff', text: `Tsunami Zone: ${consequences.inundation_radius_km}km` },
        { color: '#ffaa00', text: `Seismic: M${consequences.predicted_seismic_magnitude}` },
        { color: '#ff0000', text: 'Impact Epicenter' }
      ];

      legend.selectAll('.legend-item')
        .data(legendItems)
        .enter()
        .append('g')
        .attr('transform', (d, i) => `translate(10, ${25 + i * 18})`)
        .each(function(d) {
          d3.select(this)
            .append('circle')
            .attr('r', 6)
            .attr('fill', d.color);
          
          d3.select(this)
            .append('text')
            .attr('x', 15)
            .attr('y', 4)
            .text(d.text)
            .style('font-size', '9px')
            .style('fill', '#fff');
        });
    }

  }, [missionPlan, safeTrajectory]);

  return (
    <div className="impact-map">
      <svg ref={svgRef}></svg>
      {!missionPlan && (
        <div className="no-data-message">
          <div className="no-data-icon">🌍</div>
          <p>Analyze an asteroid to see impact predictions</p>
          <p className="no-data-subtitle">Global hazard assessment with multiple effect zones</p>
        </div>
      )}
    </div>
  );
};

export default ImpactMap;