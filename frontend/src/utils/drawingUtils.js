// src/utils/drawingUtils.js
import {
    FACEMESH_TESSELATION,
    FACEMESH_RIGHT_EYE,
    FACEMESH_RIGHT_EYEBROW,
    FACEMESH_LEFT_EYE,
    FACEMESH_LEFT_EYEBROW,
    FACEMESH_FACE_OVAL,
    FACEMESH_LIPS,
    HAND_CONNECTIONS,
    POSE_CONNECTIONS
  } from '@mediapipe/holistic'
  import * as drawingUtils from '@mediapipe/drawing_utils'
  
  /**
   * useDrawing
   * Encapsula funciones para dibujar rostro, pose y manos en un Canvas 2D.
   */
  export function useDrawing() {
    /**
     * Dibuja el rostro (468 landmarks) con malla facial y subsets (ojos, cejas, etc.)
     */
    function drawFaceLandmarks(ctx, faceLandmarks) {
      if (!faceLandmarks) return
      drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_TESSELATION, {
        color: '#C0C0C0', lineWidth: 0.5,
      })
      drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_RIGHT_EYE, {
        color: '#FF3030', lineWidth: 1,
      })
      drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_RIGHT_EYEBROW, {
        color: '#FF3030', lineWidth: 1,
      })
      drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_LEFT_EYE, {
        color: '#30FF30', lineWidth: 1,
      })
      drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_LEFT_EYEBROW, {
        color: '#30FF30', lineWidth: 1,
      })
      drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_FACE_OVAL, {
        color: '#E0E0E0', lineWidth: 1,
      })
      drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_LIPS, {
        color: '#E0E0E0', lineWidth: 1,
      })
    }
  
    /**
     * Dibuja la pose (33 landmarks)
     */
    function drawPoseLandmarks(ctx, poseLandmarks) {
      if (!poseLandmarks) return
      drawingUtils.drawConnectors(ctx, poseLandmarks, POSE_CONNECTIONS, {
        color: '#00FF00', lineWidth: 2,
      })
      drawingUtils.drawLandmarks(ctx, poseLandmarks, {
        color: '#FF0000', lineWidth: 1, radius: 3,
      })
    }
  
    /**
     * Dibuja las manos (21 landmarks)
     */
    function drawHandLandmarks(ctx, handLandmarks, colorConnectors, colorLandmarks) {
      if (!handLandmarks) return
      drawingUtils.drawConnectors(ctx, handLandmarks, HAND_CONNECTIONS, {
        color: colorConnectors, lineWidth: 3,
      })
      drawingUtils.drawLandmarks(ctx, handLandmarks, {
        color: colorLandmarks, lineWidth: 1, radius: 3,
      })
    }
  
    return {
      drawPoseLandmarks,
      drawHandLandmarks,
      drawFaceLandmarks
    }
  }
  