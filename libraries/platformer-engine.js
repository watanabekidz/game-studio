/**
 * platformer-engine.js
 * Platformer-specific helpers: entity factory, world streaming, camera,
 * and parallax backgrounds. Depends on physics-engine.js and particle-system.js.
 * Designed to be inlined into single-file HTML game output.
 *
 * Usage (after physics-engine, particle-system are inlined above this):
 *   var platformer = PlatformerEngine.setup();
 *   var player = platformer.createPlayer(120, 300, 26, 36);
 *   platformer.addGround(0, 440, 200, 60, '#334155');
 *   // Each frame:
 *   platformer.update(player, platforms, camera);
 *   platformer.renderBackground(ctx, W, H, camera);
 *   platformer.renderPlatforms(ctx, platforms, camera);
 */
var PlatformerEngine = (function() {
  'use strict';

  /**
   * Create a player entity with platformer defaults.
   */
  function createPlayer(x, y, w, h) {
    return {
      x: x || 0, y: y || 0,
      w: w || 26, h: h || 36,
      vx: 0, vy: 0,
      onGround: false,
      hitHead: false,
      coyote: 0,
      jumpHeld: false,
      dir: 1,
      reset: function(rx, ry) {
        this.x = rx || x; this.y = ry || y;
        this.vx = 0; this.vy = 0;
        this.onGround = false;
        this.hitHead = false;
        this.coyote = 0;
        this.jumpHeld = false;
      }
    };
  }

  /**
   * Camera that follows a target with optional smoothing and bounds.
   */
  function createCamera(opts) {
    opts = opts || {};
    return {
      x: 0, y: 0,
      leadX: opts.leadX || 0.3,    // target position at 30% from left
      deadZone: opts.deadZone || 0,
      smoothing: opts.smoothing || 1,  // 1 = instant, 0.1 = slow
      bounds: opts.bounds || null,      // { minX, maxX, minY, maxY }
      follow: function(target, viewW, viewH) {
        var targetX = target.x - viewW * this.leadX;
        var targetY = target.y - viewH * 0.5;
        this.x += (targetX - this.x) * this.smoothing;
        this.y += (targetY - this.y) * this.smoothing;
        if (this.bounds) {
          if (this.bounds.minX !== undefined) this.x = Math.max(this.x, this.bounds.minX);
          if (this.bounds.maxX !== undefined) this.x = Math.min(this.x, this.bounds.maxX);
          if (this.bounds.minY !== undefined) this.y = Math.max(this.y, this.bounds.minY);
          if (this.bounds.maxY !== undefined) this.y = Math.min(this.y, this.bounds.maxY);
        }
      }
    };
  }

  /**
   * Full platformer update step: horizontal movement, coyote time, jump,
   * gravity, collisions, camera. Mutates the player object.
   */
  function updatePlayer(player, input, physics, config) {
    config = config || {};
    var gravity = config.gravity || 0.55;
    var jumpForce = config.jumpForce || -10;
    var moveAccel = config.moveAccel || 0.45;
    var friction = config.friction || 0.82;
    var maxSpeed = config.maxSpeed || 5.5;
    var coyoteFrames = config.coyoteFrames || 6;
    var maxFall = config.maxFall || 12;

    // Horizontal movement
    if (input.down('a') || input.down('ArrowLeft')) { player.vx -= moveAccel; player.dir = -1; }
    if (input.down('d') || input.down('ArrowRight')) { player.vx += moveAccel; player.dir = 1; }
    player.vx *= friction;
    if (Math.abs(player.vx) > maxSpeed) {
      player.vx = maxSpeed * (player.vx > 0 ? 1 : -1);
    }

    // Coyote time
    if (player.onGround) player.coyote = coyoteFrames;
    else player.coyote--;

    // Jump
    var jumpPressed = input.down(' ') || input.down('w') || input.down('ArrowUp');
    if (jumpPressed && player.coyote > 0 && !player.jumpHeld) {
      player.vy = jumpForce;
      player.coyote = 0;
      player.jumpHeld = true;
      player.onGround = false;
    }
    if (!jumpPressed) player.jumpHeld = false;

    // Variable jump height
    if (!jumpPressed && player.vy < -3) {
      player.vy *= 0.85;
    }

    // Gravity
    physics.applyGravity(player, gravity, maxFall);

    // Move
    player.x += player.vx;
    player.y += player.vy;
  }

  /**
   * Draw a parallax mountain/ridge background layer.
   */
  function drawParallaxLayer(ctx, cameraX, viewW, viewH, config) {
    var speed = config.speed || 0.15;
    var yBase = config.yBase || viewH;
    var color = config.color || '#1e293b';
    var amp = config.amplitude || 40;
    var freq1 = config.frequency1 || 0.005;
    var freq2 = config.frequency2 || 0.012;
    var offsetY = config.offsetY || 120;
    var spacing = config.spacing || 40;
    var wrap = config.wrap || 2000;

    ctx.fillStyle = color;
    var camOff = -cameraX * speed;
    ctx.beginPath();
    ctx.moveTo(0, viewH);
    for (var x = 0; x <= viewW + 100; x += spacing) {
      var wx = (x + camOff) % wrap;
      var h = amp + Math.sin(wx * freq1) * amp * 0.5 + Math.sin(wx * freq2) * amp * 0.25;
      ctx.lineTo(x, yBase - offsetY - h);
    }
    ctx.lineTo(viewW, viewH);
    ctx.closePath();
    ctx.fill();
  }

  return {
    createPlayer: createPlayer,
    createCamera: createCamera,
    updatePlayer: updatePlayer,
    drawParallaxLayer: drawParallaxLayer
  };
})();
