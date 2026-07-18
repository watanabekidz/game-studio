/**
 * canvas-engine.js
 * DPR-aware canvas rendering with game loop, delta time, and basic tweening.
 * Designed to be inlined into single-file HTML game output.
 *
 * Usage:
 *   var engine = CanvasEngine.setup('game-canvas', 800, 600);
 *   engine.start(function(dt) {
 *     // your update/render code here
 *   });
 */
var CanvasEngine = (function() {
  'use strict';

  function setup(canvasId, width, height) {
    var canvas = document.getElementById(canvasId);
    if (!canvas) throw new Error('Canvas #' + canvasId + ' not found');

    var ctx = canvas.getContext('2d');
    var dpr = window.devicePixelRatio || 1;
    var logicalW = width;
    var logicalH = height;

    function resize() {
      canvas.width = logicalW * dpr;
      canvas.height = logicalH * dpr;
      canvas.style.width = logicalW + 'px';
      canvas.style.height = logicalH + 'px';
      ctx.scale(dpr, dpr);
    }
    resize();
    window.addEventListener('resize', resize);

    var lastTime = 0;
    var running = false;
    var updateFn = null;

    function loop(time) {
      if (!running) return;
      var dt = (time - lastTime) / 1000;
      if (dt > 0.1) dt = 0.016; // cap for large gaps
      lastTime = time;
      if (updateFn) updateFn(dt);
      requestAnimationFrame(loop);
    }

    return {
      ctx: ctx,
      width: logicalW,
      height: logicalH,
      dpr: dpr,
      start: function(fn) {
        updateFn = fn;
        running = true;
        lastTime = performance.now();
        requestAnimationFrame(loop);
      },
      stop: function() { running = false; },
      resize: resize,
      clear: function(color) {
        ctx.fillStyle = color || '#000';
        ctx.fillRect(0, 0, logicalW, logicalH);
      }
    };
  }

  return { setup: setup };
})();
