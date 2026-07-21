/**
 * particle-system.js
 * Lightweight emitter-based particle system for 2D Canvas games.
 * Designed to be inlined into single-file HTML game output.
 *
 * Usage:
 *   var particles = ParticleSystem.setup();
 *   particles.emit(100, 200, 8, '#ff0');  // burst
 *   // Each frame:
 *   particles.update();
 *   particles.render(ctx, cameraX, cameraY);
 */
var ParticleSystem = (function() {
  'use strict';

  function setup() {
    var particles = [];

    function emit(x, y, count, color, options) {
      options = options || {};
      var speed = options.speed || 3;
      var spreadX = options.spreadX || 1;
      var spreadY = options.spreadY || 1;
      var life = options.life || 40;
      var size = options.size || 3;
      var gravity = options.gravity || 0.12;

      for (var i = 0; i < count; i++) {
        particles.push({
          x: x,
          y: y,
          vx: (Math.random() - 0.5) * speed * spreadX,
          vy: -Math.random() * speed * spreadY - 1,
          life: life + Math.random() * (life * 0.5),
          maxLife: life * 1.5,
          size: size + Math.random() * (size * 0.8),
          color: color || '#fff',
          gravity: gravity
        });
      }
    }

    function update() {
      for (var i = particles.length - 1; i >= 0; i--) {
        var p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.vy += p.gravity;
        p.life--;
        if (p.life <= 0) {
          particles.splice(i, 1);
        }
      }
    }

    function render(ctx, camX, camY) {
      camX = camX || 0;
      camY = camY || 0;
      ctx.save();
      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        var alpha = Math.max(0, p.life / p.maxLife);
        ctx.globalAlpha = alpha;
        ctx.fillStyle = p.color;
        var sx = p.x - camX;
        var sy = p.y - camY;
        ctx.fillRect(sx - p.size / 2, sy - p.size / 2, p.size, p.size);
      }
      ctx.restore();
    }

    function clear() {
      particles.length = 0;
    }

    function count() {
      return particles.length;
    }

    return {
      emit: emit,
      update: update,
      render: render,
      clear: clear,
      count: count
    };
  }

  return { setup: setup };
})();
