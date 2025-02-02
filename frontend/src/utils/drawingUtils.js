//frontend/src/utils/drawingUtils.js
import {
    // FACEMESH_TESSELATION,
    // FACEMESH_RIGHT_EYE,
    // FACEMESH_RIGHT_EYEBROW,
    // FACEMESH_LEFT_EYE,
    // FACEMESH_LEFT_EYEBROW,
    // FACEMESH_LIPS,
    FACEMESH_FACE_OVAL,
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
      // drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_TESSELATION, {
      //   color: '#C0C0C0', lineWidth: 0.5,
      // })
      // drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_RIGHT_EYE, {
      //   color: '#FF3030', lineWidth: 1,
      // })
      // drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_RIGHT_EYEBROW, {
      //   color: '#FF3030', lineWidth: 1,
      // })
      // drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_LEFT_EYE, {
      //   color: '#30FF30', lineWidth: 1,
      // })
      // drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_LEFT_EYEBROW, {
      //   color: '#30FF30', lineWidth: 1,
      // })
      drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_FACE_OVAL, {
        color: '#E0E0E0', lineWidth: 2,
      })
      // drawingUtils.drawConnectors(ctx, faceLandmarks, FACEMESH_LIPS, {
      //   color: '#E0E0E0', lineWidth: 1,
      // })
    }
  
    /**
     * Dibuja la pose (33 landmarks)
     */
    // function drawPoseLandmarks(ctx, poseLandmarks) {
    //   if (!poseLandmarks) return
    //   drawingUtils.drawConnectors(ctx, poseLandmarks, POSE_CONNECTIONS, {
    //     color: '#00FF00', lineWidth: 2,
    //   })
    //   drawingUtils.drawLandmarks(ctx, poseLandmarks, {
    //     color: '#FF0000', lineWidth: 1, radius: 3,
    //   })
    // }
  /**
   * Dibuja solo los landmarks y conexiones correspondientes a la mitad superior del cuerpo.
   * En este ejemplo, se consideran los landmarks con índice menor a 23.
   */
  function drawPoseLandmarks(ctx, poseLandmarks) {
    if (!poseLandmarks) return;

    // Filtrar las conexiones: solo aquellas cuyos índices sean menores a 23.
    const upperConnections = POSE_CONNECTIONS.filter(
      ([i, j]) => i < 23 && j < 23
    );
    // Dibuja las conexiones filtradas.
    drawingUtils.drawConnectors(ctx, poseLandmarks, upperConnections, {
      color: '#00FF00',
      lineWidth: 2,
    });
    // Dibuja cada landmark de la mitad superior (índices < 23)
    for (let i = 0; i < poseLandmarks.length; i++) {
      if (i < 23) {
        const lm = poseLandmarks[i];
        drawingUtils.drawLandmarks(ctx, [lm], {
          color: '#FF0000',
          lineWidth: 1,
          radius: 3,
        });
      }
    }
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
  