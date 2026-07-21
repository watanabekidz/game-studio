/**
 * scorm-wrapper.js
 * SCORM 1.2 API wrapper for LMS communication.
 * Designed to be inlined into single-file game output for SCORM packaging.
 *
 * Usage:
 *   ScormWrapper.init('my-game-code');
 *   // On game over / score event:
 *   ScormWrapper.setScore(85);  // sets cmi.core.score.raw
 *   ScormWrapper.complete();    // sets lesson_status = "completed"
 *   ScormWrapper.finish();      // calls LMSFinish
 *
 * The wrapper detects the LMS API via window.parent (SCORM 1.2 standard)
 * and degrades gracefully when run outside an LMS (no errors thrown).
 */
var ScormWrapper = (function() {
  'use strict';

  var api = null;
  var initialized = false;
  var interactionCode = '';

  // SCORM 1.2 API discovery
  function findAPI(win) {
    var depth = 0;
    while (win && depth < 10) {
      if (win.API) return win.API;
      if (win.API_1484_11) return win.API_1484_11;
      win = win.parent;
      depth++;
    }
    return null;
  }

  return {
    /**
     * Initialize the SCORM session. Call once when the game starts.
     * @param {string} code - Unique interaction code for postMessage
     */
    init: function(code) {
      interactionCode = code || 'game';
      api = findAPI(window);
      if (api && api.LMSInitialize) {
        api.LMSInitialize('');
        initialized = true;
      }
      // Report height to parent (for LMS iframe)
      this.reportHeight();
    },

    /**
     * Report the game's height to the LMS via postMessage.
     */
    reportHeight: function() {
      var send = function() {
        var height = document.body.scrollHeight || document.documentElement.scrollHeight;
        window.parent.postMessage({
          interactionCode: interactionCode,
          type: 'SET_INSTRUCTION_HEIGHT',
          value: height
        }, '*');
      };
      window.addEventListener('load', send);
      window.addEventListener('resize', send);
      // Also send on next frame (for dynamic canvas content)
      setTimeout(send, 100);
    },

    /**
     * Set the score. Translates to cmi.core.score.raw.
     * @param {number|string} score
     * @param {number} max - Optional max score (sets cmi.core.score.max)
     */
    setScore: function(score, max) {
      if (!api || !initialized) return;
      api.LMSSetValue('cmi.core.score.raw', String(score));
      if (max !== undefined) {
        api.LMSSetValue('cmi.core.score.max', String(max));
      }
      // Report via postMessage as well (for MCG bridge)
      window.parent.postMessage({
        interactionCode: interactionCode,
        type: 'SCORM_SET_VALUE',
        key: 'cmi.core.score.raw',
        value: String(score)
      }, '*');
    },

    /**
     * Set lesson status. Translates to cmi.core.lesson_status.
     * @param {string} status - "completed" | "incomplete" | "passed" | "failed"
     */
    setStatus: function(status) {
      if (!api || !initialized) return;
      api.LMSSetValue('cmi.core.lesson_status', status);
      window.parent.postMessage({
        interactionCode: interactionCode,
        type: 'SCORM_SET_VALUE',
        key: 'cmi.core.lesson_status',
        value: status
      }, '*');
    },

    /**
     * Commit current data to the LMS. Call after setting score.
     */
    commit: function() {
      if (!api || !initialized) return;
      api.LMSCommit('');
    },

    /**
     * Mark the lesson as completed and commit.
     */
    complete: function() {
      this.setStatus('completed');
      this.commit();
    },

    /**
     * Mark the lesson as failed and commit.
     */
    fail: function() {
      this.setStatus('failed');
      this.commit();
    },

    /**
     * End the SCORM session. Call when the game finishes.
     */
    finish: function() {
      if (!api || !initialized) return;
      initialized = false;
      api.LMSFinish('');
    },

    /**
     * Convenience: set score, mark completed, commit, and finish.
     * Call this on game over.
     * @param {number} score
     * @param {number} max - Optional max score
     */
    reportComplete: function(score, max) {
      this.setScore(score, max);
      this.complete();
      this.finish();
    },

    /**
     * Check if running inside an LMS (SCORM API available).
     */
    isLMS: function() {
      return api !== null && initialized;
    }
  };
})();
