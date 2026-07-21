/**
 * input-handler.js
 * Unified keyboard input with key tracking, bindings, and repeat protection.
 * Designed to be inlined into single-file HTML game output.
 *
 * Usage:
 *   var input = InputHandler.setup();
 *   // Check state per frame:
 *   if (input.down('a') || input.down('ArrowLeft')) moveLeft();
 *   // One-shot (fires once per press):
 *   if (input.justPressed(' ')) jump();
 *   if (input.justPressed('r')) restart();
 */
var InputHandler = (function() {
  'use strict';

  function setup() {
    var held = {};          // currently held keys
    var justDown = {};      // true for one frame after press
    var justUp = {};        // true for one frame after release
    var prevHeld = {};      // previous frame's state

    function normalize(key) {
      return key.length === 1 ? key.toLowerCase() : key;
    }

    function onDown(e) {
      var k = normalize(e.key);
      if (!held[k]) {
        held[k] = true;
        justDown[k] = true;
      }
      // Prevent scroll on game keys
      if (k === ' ' || k === 'ArrowUp' || k === 'ArrowDown' ||
          k === 'ArrowLeft' || k === 'ArrowRight') {
        e.preventDefault();
      }
    }

    function onUp(e) {
      var k = normalize(e.key);
      if (held[k]) {
        held[k] = false;
        justUp[k] = true;
      }
    }

    window.addEventListener('keydown', onDown);
    window.addEventListener('keyup', onUp);

    function update() {
      // justPressed: true only on the frame the key was first pressed
      // justReleased: true only on the frame the key was released
      for (var k in justDown) justDown[k] = false;
      for (var k in justUp) justUp[k] = false;
      // Carry forward any that haven't been consumed yet
      for (var k in held) if (held[k] && !prevHeld[k]) justDown[k] = true;
      for (var k in prevHeld) if (prevHeld[k] && !held[k]) justUp[k] = true;
      // Snapshot for next frame
      for (var k in held) prevHeld[k] = held[k];
      for (var k in prevHeld) if (!held[k] && !justUp[k]) delete prevHeld[k];
    }

    function pressed(key) { return !!held[normalize(key)]; }
    function justPressed(key) { return !!justDown[normalize(key)]; }
    function justReleased(key) { return !!justUp[normalize(key)]; }

    return {
      down: pressed,         // held down this frame
      justPressed: justPressed,
      justReleased: justReleased,
      update: update,         // call once per frame before reading state
      destroy: function() {
        window.removeEventListener('keydown', onDown);
        window.removeEventListener('keyup', onUp);
      }
    };
  }

  return { setup: setup };
})();
