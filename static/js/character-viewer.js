class CharacterViewer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);

    // Force initial size
    this.canvas.style.width = "400px";
    this.canvas.style.height = "400px";
    this.canvas.width = 400;
    this.canvas.height = 400;

    // Initialize scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x000000);

    // Initialize camera
    this.camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
    this.camera.position.set(0, 0, 5);

    // Initialize renderer
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
    });
    this.renderer.setSize(400, 400, false);
    this.renderer.shadowMap.enabled = true;

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    this.scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    directionalLight.castShadow = true;
    this.scene.add(directionalLight);

    const backLight = new THREE.DirectionalLight(0xffffff, 0.3);
    backLight.position.set(-5, 5, -5);
    this.scene.add(backLight);

    // Add cube
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshPhongMaterial({
      color: 0x049ef4,
      shininess: 60,
      specular: 0x049ef4,
    });
    this.cube = new THREE.Mesh(geometry, material);
    this.scene.add(this.cube);

    // Add controls
    this.controls = new THREE.OrbitControls(
      this.camera,
      this.renderer.domElement
    );
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.screenSpacePanning = false;
    this.controls.minDistance = 3;
    this.controls.maxDistance = 8;

    // Add resize observer
    this.resizeObserver = new ResizeObserver(() => {
      this.onWindowResize();
    });
    this.resizeObserver.observe(this.canvas.parentElement);

    // Start animation loop
    this.animate();

    // Force initial render
    this.renderer.render(this.scene, this.camera);
  }

  onWindowResize() {
    // Keep aspect ratio 1:1
    const width = 400;
    const height = 400;

    this.canvas.style.width = `${width}px`;
    this.canvas.style.height = `${height}px`;
    this.canvas.width = width;
    this.canvas.height = height;

    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height, false);

    // Force a render update
    this.renderer.render(this.scene, this.camera);
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    // Rotate cube
    this.cube.rotation.x += 0.005;
    this.cube.rotation.y += 0.01;

    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }

  // Placeholder method for future character loading
  loadCharacter(raceId, classId) {
    console.log("Loading character:", { raceId, classId });

    // Update cube color based on class
    const classColors = {
      1: 0xc79c6e, // Warrior - tan
      2: 0xf58cba, // Paladin - pink
      3: 0xabd473, // Hunter - green
      4: 0xfff569, // Rogue - yellow
      5: 0xffffff, // Priest - white
      6: 0xc41f3b, // Death Knight - red
      7: 0x0070de, // Shaman - blue
      8: 0x69ccf0, // Mage - light blue
      9: 0x9482c9, // Warlock - purple
      11: 0xff7d0a, // Druid - orange
    };

    const color = classColors[classId] || 0x049ef4;
    this.cube.material.color.setHex(color);
    this.cube.material.specular.setHex(color);

    // Force a render update
    this.renderer.render(this.scene, this.camera);
  }
}
