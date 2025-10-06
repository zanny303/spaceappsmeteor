// src/components/SolarSystem3D.js - FIXED VERSION
import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const SolarSystem3D = ({ missionPlan, safeTrajectory, realTimeDeflection, loading }) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const animationRef = useRef(null);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, mountRef.current.clientWidth / mountRef.current.clientHeight, 0.1, 1000000);
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true, 
      alpha: true,
      powerPreference: "high-performance"
    });
    
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.setClearColor(0x000011, 1);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mountRef.current.appendChild(renderer.domElement);

    // Enhanced controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 50;
    controls.maxDistance = 5000;
    controls.autoRotate = false;

    // Enhanced lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const sunLight = new THREE.PointLight(0xffff00, 2, 100000);
    sunLight.position.set(0, 0, 0);
    sunLight.castShadow = true;
    scene.add(sunLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1000, 1000, 1000);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // Create solar system
    createSolarSystem(scene);

    // Position camera for better view
    camera.position.set(0, 300, 800);
    controls.update();

    // Animation loop
    const animate = () => {
      animationRef.current = requestAnimationFrame(animate);
      controls.update();
      
      // Rotate Earth and other bodies
      const earth = scene.getObjectByName('earth');
      if (earth) earth.rotation.y += 0.005;
      
      const asteroid = scene.getObjectByName('asteroid');
      if (asteroid) asteroid.rotation.y += 0.01;
      
      renderer.render(scene, camera);
    };
    animate();

    sceneRef.current = scene;
    rendererRef.current = renderer;
    setIsInitialized(true);

    // Handle resize
    const handleResize = () => {
      if (!mountRef.current) return;
      const width = mountRef.current.clientWidth;
      const height = mountRef.current.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (mountRef.current && rendererRef.current) {
        mountRef.current.removeChild(rendererRef.current.domElement);
      }
      renderer.dispose();
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  // Update trajectories when mission plan changes
  useEffect(() => {
    if (sceneRef.current && missionPlan && isInitialized) {
      updateTrajectories(sceneRef.current, missionPlan, safeTrajectory, realTimeDeflection);
    }
  }, [missionPlan, safeTrajectory, realTimeDeflection, isInitialized]);

  const createSolarSystem = (scene) => {
    // Sun with glow effect
    const sunGeometry = new THREE.SphereGeometry(20, 32, 32);
    const sunMaterial = new THREE.MeshBasicMaterial({ 
      color: 0xffff00,
      emissive: 0xffff00,
      emissiveIntensity: 0.8
    });
    const sun = new THREE.Mesh(sunGeometry, sunMaterial);
    sun.name = 'sun';
    scene.add(sun);

    // Earth with enhanced details
    const earthGeometry = new THREE.SphereGeometry(6, 32, 32);
    const earthMaterial = new THREE.MeshStandardMaterial({ 
      color: 0x2233ff,
      emissive: 0x112266,
      emissiveIntensity: 0.2,
      roughness: 0.8,
      metalness: 0.2
    });
    const earth = new THREE.Mesh(earthGeometry, earthMaterial);
    earth.position.set(150, 0, 0); // 150 units = 1 AU
    earth.name = 'earth';
    earth.castShadow = true;
    earth.receiveShadow = true;
    scene.add(earth);

    // Earth orbit ring
    const earthOrbitGeometry = new THREE.RingGeometry(148, 152, 64);
    const earthOrbitMaterial = new THREE.MeshBasicMaterial({ 
      color: 0x4444ff, 
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.1
    });
    const earthOrbit = new THREE.Mesh(earthOrbitGeometry, earthOrbitMaterial);
    earthOrbit.rotation.x = Math.PI / 2;
    earthOrbit.name = 'earth-orbit';
    scene.add(earthOrbit);

    // Add coordinate axes for reference
    const axesHelper = new THREE.AxesHelper(100);
    scene.add(axesHelper);

    // Add some stars in background
    addStars(scene);
  };

  const addStars = (scene) => {
    const starGeometry = new THREE.BufferGeometry();
    const starPositions = [];
    
    for (let i = 0; i < 2000; i++) {
      const radius = 2000 + Math.random() * 3000;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      
      const x = radius * Math.sin(phi) * Math.cos(theta);
      const y = radius * Math.sin(phi) * Math.sin(theta);
      const z = radius * Math.cos(phi);
      
      starPositions.push(x, y, z);
    }
    
    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starPositions, 3));
    const starMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 2,
      transparent: true,
      opacity: 0.8
    });
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);
  };

  const updateTrajectories = (scene, missionPlan, safeTrajectory, realTimeDeflection) => {
    console.log("🔄 Updating 3D visualization...");

    // CRITICAL FIX: Use correct scale - Backend sends km, Earth is at 1 AU = 1.496e8 km = 150 units
    const SCALE = 1e6; // 1 million km per unit (so 150M km / 1M = 150 units for Earth)

    // Clear previous trajectories and markers
    scene.children = scene.children.filter(child =>
      !child.userData?.isTrajectory &&
      !child.userData?.isAsteroid &&
      !child.userData?.isImpact &&
      !child.userData?.isMarker &&
      !child.userData?.isCloseApproach
    );

    // FIXED: Plot hazard corridor (original trajectories from NASA/JPL data)
    if (missionPlan.visualization_data?.hazard_corridor) {
      console.log("📈 Plotting hazard corridor...");
      const corridorData = missionPlan.visualization_data.hazard_corridor;
      console.log(`   Found ${corridorData.length} trajectory simulations`);

      corridorData.forEach((trajectory, index) => {
        if (trajectory && trajectory.length > 0) {
          // FIXED: Validate and filter trajectory points
          const validPoints = trajectory.filter(coord => 
            coord && coord.length === 3 && 
            !isNaN(coord[0]) && !isNaN(coord[1]) && !isNaN(coord[2]) &&
            isFinite(coord[0]) && isFinite(coord[1]) && isFinite(coord[2])
          );

          if (validPoints.length > 1) {
            const points = validPoints.map(coord =>
              new THREE.Vector3(coord[0] / SCALE, coord[1] / SCALE, coord[2] / SCALE)
            );

            if (index === 0) {
              console.log(`   Nominal trajectory: ${validPoints.length} valid points`);
              console.log(`   First point (km): [${validPoints[0][0].toExponential(2)}, ${validPoints[0][1].toExponential(2)}, ${validPoints[0][2].toExponential(2)}]`);
              console.log(`   First point (units): [${(validPoints[0][0]/SCALE).toFixed(2)}, ${(validPoints[0][1]/SCALE).toFixed(2)}, ${(validPoints[0][2]/SCALE).toFixed(2)}]`);
            }

            const trajectoryGeometry = new THREE.BufferGeometry().setFromPoints(points);
            const trajectoryMaterial = new THREE.LineBasicMaterial({
              color: index === 0 ? 0xff4444 : 0xff8888,
              transparent: true,
              opacity: index === 0 ? 0.9 : 0.3,
              linewidth: index === 0 ? 2 : 1
            });

            const trajectoryLine = new THREE.Line(trajectoryGeometry, trajectoryMaterial);
            trajectoryLine.userData = { isTrajectory: true, trajectoryIndex: index, type: 'nominal' };
            scene.add(trajectoryLine);

            // Highlight Earth-crossing region for nominal trajectory
            if (index === 0) {
              highlightEarthCrossingRegion(scene, points, 0xff4444, 'nominal');
            }
          } else {
            console.warn(`   Skipping trajectory ${index}: insufficient valid points (${validPoints.length})`);
          }
        }
      });
      console.log("   ✅ Hazard corridor plotted");
    }

    // FIXED: Plot safe trajectory after full simulation (green) - with enhanced visibility
    if (safeTrajectory && safeTrajectory.length > 0) {
      console.log("🟢 Plotting safe trajectory (full simulation)...");
      console.log(`   Points: ${safeTrajectory.length}`);
      
      const validPoints = safeTrajectory.filter(coord => 
        coord && coord.length === 3 && 
        !isNaN(coord[0]) && !isNaN(coord[1]) && !isNaN(coord[2]) &&
        isFinite(coord[0]) && isFinite(coord[1]) && isFinite(coord[2])
      );

      if (validPoints.length > 1) {
        const safePoints = validPoints.map(coord =>
          new THREE.Vector3(coord[0] / SCALE, coord[1] / SCALE, coord[2] / SCALE)
        );

        // Main trajectory line
        const safeGeometry = new THREE.BufferGeometry().setFromPoints(safePoints);
        const safeMaterial = new THREE.LineBasicMaterial({
          color: 0x44ff44,
          linewidth: 3,
          transparent: true,
          opacity: 0.9
        });

        const safeLine = new THREE.Line(safeGeometry, safeMaterial);
        safeLine.userData = { isTrajectory: true, isSafe: true, type: 'safe' };
        scene.add(safeLine);

        // Add glow effect to make it more visible
        const safeGlowGeometry = new THREE.BufferGeometry().setFromPoints(safePoints);
        const safeGlowMaterial = new THREE.LineBasicMaterial({
          color: 0x44ff44,
          linewidth: 6,
          transparent: true,
          opacity: 0.3
        });
        const safeGlow = new THREE.Line(safeGlowGeometry, safeGlowMaterial);
        safeGlow.userData = { isTrajectory: true, type: 'safe-glow' };
        scene.add(safeGlow);

        // Highlight Earth-crossing region
        highlightEarthCrossingRegion(scene, safePoints, 0x44ff44, 'safe');

        console.log(`   ✅ Safe trajectory plotted with ${validPoints.length} points`);
      } else {
        console.warn(`   ⚠️ Safe trajectory has insufficient valid points: ${validPoints.length}`);
      }
    }

    // FIXED: Plot real-time deflection trajectory (yellow) - with enhanced visibility
    if (realTimeDeflection && realTimeDeflection.length > 0) {
      console.log("🟡 Plotting real-time deflection preview...");
      console.log(`   Points: ${realTimeDeflection.length}`);
      
      const validPoints = realTimeDeflection.filter(coord => 
        coord && coord.length === 3 && 
        !isNaN(coord[0]) && !isNaN(coord[1]) && !isNaN(coord[2]) &&
        isFinite(coord[0]) && isFinite(coord[1]) && isFinite(coord[2])
      );

      if (validPoints.length > 1) {
        const realTimePoints = validPoints.map(coord =>
          new THREE.Vector3(coord[0] / SCALE, coord[1] / SCALE, coord[2] / SCALE)
        );

        // Main trajectory line
        const realTimeGeometry = new THREE.BufferGeometry().setFromPoints(realTimePoints);
        const realTimeMaterial = new THREE.LineBasicMaterial({
          color: 0xffff00,
          linewidth: 4,
          transparent: true,
          opacity: 0.95
        });

        const realTimeLine = new THREE.Line(realTimeGeometry, realTimeMaterial);
        realTimeLine.userData = { isTrajectory: true, isRealTime: true, type: 'realtime' };
        scene.add(realTimeLine);

        // Add glow effect
        const realtimeGlowGeometry = new THREE.BufferGeometry().setFromPoints(realTimePoints);
        const realtimeGlowMaterial = new THREE.LineBasicMaterial({
          color: 0xffff00,
          linewidth: 8,
          transparent: true,
          opacity: 0.4
        });
        const realtimeGlow = new THREE.Line(realtimeGlowGeometry, realtimeGlowMaterial);
        realtimeGlow.userData = { isTrajectory: true, type: 'realtime-glow' };
        scene.add(realtimeGlow);

        // Highlight Earth-crossing region
        highlightEarthCrossingRegion(scene, realTimePoints, 0xffff00, 'realtime');

        console.log(`   ✅ Real-time deflection plotted with ${validPoints.length} points`);
      } else {
        console.warn(`   ⚠️ Real-time deflection has insufficient valid points: ${validPoints.length}`);
      }
    }

    // FIXED: Add asteroid marker at current position
    if (missionPlan.initial_state_vector) {
      console.log("🪨 Adding asteroid marker...");
      const [x, y, z] = missionPlan.initial_state_vector;

      // Validate state vector
      if (!isNaN(x) && !isNaN(y) && !isNaN(z) && isFinite(x) && isFinite(y) && isFinite(z)) {
        // Asteroid mesh with glow
        const asteroidGeometry = new THREE.SphereGeometry(4, 16, 16);
        const asteroidMaterial = new THREE.MeshStandardMaterial({
          color: 0xff6600,
          emissive: 0xff3300,
          emissiveIntensity: 0.8,
          roughness: 0.7,
          metalness: 0.3
        });
        const asteroid = new THREE.Mesh(asteroidGeometry, asteroidMaterial);
        asteroid.position.set(x / SCALE, y / SCALE, z / SCALE);
        asteroid.userData = { isAsteroid: true };
        asteroid.name = 'asteroid';
        asteroid.castShadow = true;
        scene.add(asteroid);

        // Add pulsing glow around asteroid
        const glowGeometry = new THREE.SphereGeometry(7, 16, 16);
        const glowMaterial = new THREE.MeshBasicMaterial({
          color: 0xff6600,
          transparent: true,
          opacity: 0.3
        });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        glow.position.copy(asteroid.position);
        glow.userData = { isAsteroid: true };
        scene.add(glow);

        // Animate glow
        const animateGlow = () => {
          if (glow.parent) {
            const scale = 1 + Math.sin(Date.now() * 0.002) * 0.3;
            glow.scale.set(scale, scale, scale);
            requestAnimationFrame(animateGlow);
          }
        };
        animateGlow();

        console.log(`   Position (km): [${x.toExponential(2)}, ${y.toExponential(2)}, ${z.toExponential(2)}]`);
        console.log(`   Position (units): [${(x/SCALE).toFixed(2)}, ${(y/SCALE).toFixed(2)}, ${(z/SCALE).toFixed(2)}]`);

        // Draw line from asteroid to closest trajectory point
        if (missionPlan.visualization_data?.hazard_corridor?.[0]) {
          const firstTrajectory = missionPlan.visualization_data.hazard_corridor[0];
          if (firstTrajectory.length > 0) {
            const firstPoint = firstTrajectory[0];
            const lineGeometry = new THREE.BufferGeometry().setFromPoints([
              asteroid.position,
              new THREE.Vector3(firstPoint[0] / SCALE, firstPoint[1] / SCALE, firstPoint[2] / SCALE)
            ]);
            const lineMaterial = new THREE.LineBasicMaterial({
              color: 0xff6600,
              transparent: true,
              opacity: 0.5,
              linewidth: 2
            });
            const connectionLine = new THREE.Line(lineGeometry, lineMaterial);
            connectionLine.userData = { isMarker: true };
            scene.add(connectionLine);
          }
        }
      } else {
        console.error(`   ❌ Invalid state vector: [${x}, ${y}, ${z}]`);
      }
    }

    console.log("✅ 3D visualization updated");
  };

  // Helper function to highlight Earth-crossing region
  const highlightEarthCrossingRegion = (scene, trajectoryPoints, color, type) => {
    const earthPosition = new THREE.Vector3(150, 0, 0);
    const earthInfluenceRadius = 50; // Zone around Earth to highlight

    // Find points near Earth
    const nearEarthPoints = [];
    trajectoryPoints.forEach((point, index) => {
      const distanceToEarth = point.distanceTo(earthPosition);
      if (distanceToEarth < earthInfluenceRadius) {
        nearEarthPoints.push(point);
      }
    });

    if (nearEarthPoints.length > 1) {
      // Create highlighted segment
      const highlightGeometry = new THREE.BufferGeometry().setFromPoints(nearEarthPoints);
      const highlightMaterial = new THREE.LineBasicMaterial({
        color: color,
        linewidth: 8,
        transparent: true,
        opacity: 1.0
      });
      const highlightLine = new THREE.Line(highlightGeometry, highlightMaterial);
      highlightLine.userData = { isCloseApproach: true, type: `${type}-approach` };
      scene.add(highlightLine);

      // Add pulsing sphere at closest approach
      const closestPoint = nearEarthPoints.reduce((closest, point) => {
        const distToCurrent = point.distanceTo(earthPosition);
        const distToClosest = closest.distanceTo(earthPosition);
        return distToCurrent < distToClosest ? point : closest;
      }, nearEarthPoints[0]);

      const approachMarker = new THREE.Mesh(
        new THREE.SphereGeometry(3, 16, 16),
        new THREE.MeshBasicMaterial({
          color: color,
          transparent: true,
          opacity: 0.8
        })
      );
      approachMarker.position.copy(closestPoint);
      approachMarker.userData = { isCloseApproach: true, isPulsing: true };
      scene.add(approachMarker);

      // Animate pulsing
      const animatePulse = () => {
        if (approachMarker.parent) {
          const scale = 1 + Math.sin(Date.now() * 0.003) * 0.5;
          approachMarker.scale.set(scale, scale, scale);
          requestAnimationFrame(animatePulse);
        }
      };
      animatePulse();

      console.log(`   Highlighted ${nearEarthPoints.length} points near Earth for ${type} trajectory`);
    }
  };

  return (
    <div className="solar-system-3d">
      <div ref={mountRef} className="three-container" />
      <div className="visualization-controls">
        <div className="legend">
          <div className="legend-item">
            <div className="color-box red"></div>
            <span>Original Hazard Trajectory</span>
          </div>
          <div className="legend-item">
            <div className="color-box yellow"></div>
            <span>Real-time Deflection Preview</span>
          </div>
          <div className="legend-item">
            <div className="color-box green"></div>
            <span>Safe Trajectory (Full Sim)</span>
          </div>
          <div className="legend-item">
            <div className="color-box orange"></div>
            <span>Asteroid (pulsing glow)</span>
          </div>
          <div className="legend-item">
            <div className="color-box blue"></div>
            <span>Earth</span>
          </div>
          <div className="legend-item">
            <div className="color-box purple"></div>
            <span>Close Approach Markers</span>
          </div>
        </div>
        <div className="controls-info">
          <p>🖱️ Click and drag to rotate • Scroll to zoom • Right-click to pan</p>
          {loading && <div className="loading-text">🔄 Updating visualization...</div>}
          {missionPlan && (
            <div className="mission-info">
              <strong>Viewing: {missionPlan.asteroid_info.name}</strong>
              <br />
              Data Sources: {missionPlan.asteroid_info.data_sources?.join(', ') || 'Sample Data'}
              {realTimeDeflection && <div className="deflection-active">⚡ Real-time deflection preview active</div>}
              {safeTrajectory && <div className="simulation-complete">✅ Full simulation complete</div>}
              <div className="visualization-tip">
                💡 Tip: Look for pulsing markers near Earth - they show close approach points
              </div>
            </div>
          )}
        </div>
      </div>
      
      {!missionPlan && (
        <div className="no-data-overlay">
          <div className="no-data-content">
            <div className="planet-icon">🪐</div>
            <h3>Solar System Visualization</h3>
            <p>Analyze an asteroid to see orbital trajectories and impact predictions</p>
            <div className="hint">
              Try analyzing Apophis, Bennu, or Itokawa to get started
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SolarSystem3D;