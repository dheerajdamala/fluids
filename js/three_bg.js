/**
 * Three-Dimensional Spatial Background & Interactive 3D Card Dynamics
 * Provides an ambient WebGL / 3D Canvas perspective environment
 * with mouse-tracking parallax, wave dynamics, and realistic physical tilt.
 */

(function () {
  let scene, camera, renderer, gridMesh, particleSystem;
  let mouseX = 0, mouseY = 0;
  let targetRotX = 0, targetRotY = 0;
  let width = window.innerWidth;
  let height = window.innerHeight;
  let animId = null;

  document.addEventListener("DOMContentLoaded", () => {
    init3DBackground();
    init3DCardTilt();
    initIsometricToggle();
  });

  function init3DBackground() {
    const canvas = document.getElementById("bg3dCanvas");
    if (!canvas) return;

    if (typeof THREE !== "undefined") {
      try {
        initThreeJS(canvas);
        return;
      } catch (err) {
        console.warn("Three.js init failed, falling back to 3D Canvas:", err);
      }
    }
    // Fallback: Custom 3D Isometric Grid via Canvas 2D
    initCanvas3DFallback(canvas);
  }

  // ------------------ Three.js Engine ------------------
  function initThreeJS(canvas) {
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x08090f, 0.0018);

    camera = new THREE.PerspectiveCamera(60, width / height, 1, 3000);
    camera.position.set(0, 280, 520);
    camera.lookAt(0, -50, 0);

    renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(width, height);

    // 3D Terrain Grid
    const gridGeo = new THREE.PlaneGeometry(1600, 1600, 48, 48);
    gridGeo.rotateX(-Math.PI / 2);

    // Add gentle terrain elevation variation
    const pos = gridGeo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      const dist = Math.sqrt(x * x + z * z);
      const elevation = Math.sin(x * 0.008) * Math.cos(z * 0.008) * 35 - (dist * 0.04);
      pos.setY(i, elevation);
    }
    gridGeo.computeVertexNormals();

    const gridMat = new THREE.MeshBasicMaterial({
      color: 0x1d273d,
      wireframe: true,
      transparent: true,
      opacity: 0.35
    });
    gridMesh = new THREE.Mesh(gridGeo, gridMat);
    gridMesh.position.y = -120;
    scene.add(gridMesh);

    // Floating 3D Node Constellation
    const particleCount = 200;
    const pGeo = new THREE.BufferGeometry();
    const pPositions = new Float32Array(particleCount * 3);
    const pVelocities = [];

    for (let i = 0; i < particleCount * 3; i += 3) {
      pPositions[i] = (Math.random() - 0.5) * 1400;
      pPositions[i + 1] = Math.random() * 320 - 80;
      pPositions[i + 2] = (Math.random() - 0.5) * 1200;
      pVelocities.push({
        vx: (Math.random() - 0.5) * 0.2,
        vy: (Math.random() - 0.5) * 0.15,
        vz: (Math.random() - 0.5) * 0.2
      });
    }
    pGeo.setAttribute("position", new THREE.BufferAttribute(pPositions, 3));

    const pMat = new THREE.PointsMaterial({
      color: 0x38bdf8,
      size: 3.5,
      transparent: true,
      opacity: 0.75,
      blending: THREE.AdditiveBlending
    });
    particleSystem = new THREE.Points(pGeo, pMat);
    scene.add(particleSystem);

    // Mouse Tracking
    window.addEventListener("mousemove", (e) => {
      mouseX = (e.clientX - width / 2) * 0.001;
      mouseY = (e.clientY - height / 2) * 0.001;
    });

    window.addEventListener("resize", () => {
      width = window.innerWidth;
      height = window.innerHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    });

    let clock = 0;
    function renderLoop() {
      clock += 0.008;

      // Subtle dynamic wave motion
      if (gridMesh) {
        gridMesh.rotation.y = Math.sin(clock * 0.2) * 0.04;
      }

      // Parallax smooth interpolation
      targetRotY += (mouseX * 0.35 - targetRotY) * 0.04;
      targetRotX += (mouseY * 0.2 - targetRotX) * 0.04;

      camera.position.x = Math.sin(targetRotY) * 520;
      camera.position.z = Math.cos(targetRotY) * 520;
      camera.position.y = 280 + targetRotX * 180;
      camera.lookAt(0, -60, 0);

      // Drift particles
      if (particleSystem) {
        const positions = particleSystem.geometry.attributes.position.array;
        for (let i = 0; i < particleCount; i++) {
          positions[i * 3 + 1] += pVelocities[i].vy;
          if (positions[i * 3 + 1] > 260) positions[i * 3 + 1] = -60;
          if (positions[i * 3 + 1] < -60) positions[i * 3 + 1] = 260;
        }
        particleSystem.geometry.attributes.position.needsUpdate = true;
      }

      renderer.render(scene, camera);
      animId = requestAnimationFrame(renderLoop);
    }
    renderLoop();
  }

  // ------------------ Canvas 2D 3D-Perspective Fallback ------------------
  function initCanvas3DFallback(canvas) {
    const ctx = canvas.getContext("2d");
    canvas.width = width;
    canvas.height = height;

    window.addEventListener("resize", () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
    });

    let offset = 0;
    window.addEventListener("mousemove", (e) => {
      mouseX = (e.clientX / width - 0.5) * 2;
      mouseY = (e.clientY / height - 0.5) * 2;
    });

    function drawGrid3D() {
      ctx.clearRect(0, 0, width, height);

      const horizon = height * 0.42 + mouseY * 25;
      const fov = 320;
      const vpX = width * 0.5 + mouseX * 45;

      ctx.save();
      ctx.strokeStyle = "rgba(45, 65, 102, 0.25)";
      ctx.lineWidth = 1;

      // Perspective Depth Lines
      const cols = 28;
      for (let c = -cols; c <= cols; c++) {
        const xFloor = c * 60;
        ctx.beginPath();
        ctx.moveTo(vpX, horizon);
        const groundX = vpX + (xFloor * (height - horizon)) / fov;
        ctx.lineTo(groundX, height);
        ctx.stroke();
      }

      // Horizontal Latitudinal Rungs
      offset = (offset + 0.35) % 40;
      for (let z = 40 + offset; z < height - horizon; z += 35) {
        const y = horizon + Math.pow(z / (height - horizon), 1.8) * (height - horizon);
        const alpha = Math.min(0.3, Math.max(0.04, (y - horizon) / (height - horizon) * 0.35));
        ctx.strokeStyle = `rgba(56, 189, 248, ${alpha})`;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }
      ctx.restore();

      requestAnimationFrame(drawGrid3D);
    }
    drawGrid3D();
  }

  // ------------------ Interactive 3D Tilt for Cards ------------------
  function init3DCardTilt() {
    const tiltCards = document.querySelectorAll(".tilt-3d");

    tiltCards.forEach((card) => {
      // Add specular reflection sheen layer if not exists
      if (!card.querySelector(".card-sheen")) {
        const sheen = document.createElement("div");
        sheen.className = "card-sheen";
        card.appendChild(sheen);
      }

      card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const cardX = e.clientX - rect.left;
        const cardY = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotX = ((cardY - centerY) / centerY) * -9.5; // Max 9.5 deg
        const rotY = ((cardX - centerX) / centerX) * 9.5;

        card.style.transform = `perspective(1000px) rotateX(${rotX.toFixed(2)}deg) rotateY(${rotY.toFixed(2)}deg) translateZ(12px)`;

        const sheen = card.querySelector(".card-sheen");
        if (sheen) {
          const px = (cardX / rect.width) * 100;
          const py = (cardY / rect.height) * 100;
          sheen.style.background = `radial-gradient(circle at ${px}% ${py}%, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0) 65%)`;
          sheen.style.opacity = "1";
        }
      });

      card.addEventListener("mouseleave", () => {
        card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)";
        const sheen = card.querySelector(".card-sheen");
        if (sheen) sheen.style.opacity = "0";
      });
    });
  }

  // ------------------ 3D Isometric View Toggle for Maze Stage ------------------
  function initIsometricToggle() {
    const btnIso = document.getElementById("btnToggle3DMaze");
    const canvasWrap = document.querySelector("#page-ai .canvas-wrapper");
    if (!btnIso || !canvasWrap) return;

    let is3D = false;
    btnIso.addEventListener("click", () => {
      is3D = !is3D;
      if (is3D) {
        canvasWrap.classList.add("iso-perspective-3d");
        btnIso.classList.add("active");
        btnIso.innerHTML = `
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
          Switch to Planar (2D)
        `;
      } else {
        canvasWrap.classList.remove("iso-perspective-3d");
        btnIso.classList.remove("active");
        btnIso.innerHTML = `
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
          Perspective (3D)
        `;
      }
    });
  }

  // Expose global re-init if DOM changes
  window.reinit3DCardTilt = init3DCardTilt;
})();
