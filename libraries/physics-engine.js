/**
 * physics-engine.js
 * AABB collision detection and resolution for 2D platformers.
 * Designed to be inlined into single-file HTML game output.
 *
 * Usage:
 *   var physics = PhysicsEngine.setup();
 *   physics.addSolid({ x: 0, y: 440, w: 800, h: 60 });  // ground
 *   // Each frame:
 *   physics.resolve(entity, solids);
 *   // entity.onGround is set to true if landed this frame
 */
var PhysicsEngine = (function() {
  'use strict';

  function aabb(ax, ay, aw, ah, bx, by, bw, bh) {
    return ax < bx + bw && ax + aw > bx && ay < by + bh && ay + ah > by;
  }

  /**
   * Resolve collisions between an entity and an array of solid rectangles.
   * Mutates entity.x, entity.y, entity.vx, entity.vy in place.
   * Sets entity.onGround to true if the entity is resting on top of a solid.
   * Sets entity.hitHead to true if the entity bumped its head.
   *
   * @param {Object} entity  — { x, y, w, h, vx, vy }
   * @param {Array} solids   — [{ x, y, w, h }, ...]
   */
  function resolve(entity, solids) {
    entity.onGround = false;
    entity.hitHead = false;

    for (var i = 0; i < solids.length; i++) {
      var s = solids[i];
      if (!aabb(entity.x, entity.y, entity.w, entity.h, s.x, s.y, s.w, s.h)) continue;

      var overlapLeft  = (entity.x + entity.w) - s.x;
      var overlapRight = (s.x + s.w) - entity.x;
      var overlapTop   = (entity.y + entity.h) - s.y;
      var overlapBot   = (s.y + s.h) - entity.y;

      var minX = Math.min(overlapLeft, overlapRight);
      var minY = Math.min(overlapTop, overlapBot);

      if (minY < minX) {
        // Resolve vertically
        if (overlapTop < overlapBot) {
          // Landing on top
          entity.y = s.y - entity.h;
          entity.vy = 0;
          entity.onGround = true;
        } else {
          // Head bump
          entity.y = s.y + s.h;
          entity.vy = 0;
          entity.hitHead = true;
        }
      } else {
        // Resolve horizontally
        if (overlapLeft < overlapRight) {
          entity.x = s.x - entity.w;
        } else {
          entity.x = s.x + s.w;
        }
        entity.vx = 0;
      }
    }
  }

  /**
   * Apply gravity to an entity. Call before movement each frame.
   * @param {Object} entity — mutated: entity.vy += gravity
   * @param {Number} gravity — e.g. 0.55
   * @param {Number} maxFall — terminal velocity cap, e.g. 12
   */
  function applyGravity(entity, gravity, maxFall) {
    entity.vy += gravity;
    if (entity.vy > maxFall) entity.vy = maxFall;
  }

  return {
    aabb: aabb,
    resolve: resolve,
    applyGravity: applyGravity
  };
})();
