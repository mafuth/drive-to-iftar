import type { Material, Mesh, Object3D } from 'three';
import { GAME_CONFIG } from '$lib/config';

// Shared uniform object so all materials reference the same curvature value
export const globalUniforms = {
    uCurvature: { value: GAME_CONFIG.world.curvature }
};

export function updateGlobalCurvature(val: number) {
    globalUniforms.uCurvature.value = val;
}

export function applyWorldCurvature(object: Object3D) {
    object.traverse((child) => {
        if ((child as Mesh).isMesh) {
            const mesh = child as Mesh;
            const material = mesh.material as Material;

            // Handle array of materials
            const materials = Array.isArray(material) ? material : [material];

            materials.forEach((mat: any) => {
                // Compile Check
                if (mat.userData.hasCurvature) return;
                mat.userData.hasCurvature = true;

                // console.log("Injecting Curvature into Material:", mat.name || "Unnamed");

                mat.onBeforeCompile = (shader: any) => {
                    // console.log("Compiling shader for:", mat.name || "Unnamed");

                    // Assign shared uniform
                    shader.uniforms.uCurvature = globalUniforms.uCurvature;

                    // Inject uniform definition
                    shader.vertexShader = `uniform float uCurvature;\n` + shader.vertexShader;

                    // Inject bending logic
                    shader.vertexShader = shader.vertexShader.replace(
                        '#include <project_vertex>',
                        `
                        #include <project_vertex>
                        // mvPosition is View Space. Forward is -Z.
                        
                        float zDist = mvPosition.z; 
                        
                        // Use standard formula: y = y + (z * z * curvature)
                        mvPosition.y = mvPosition.y + (zDist * zDist * uCurvature);

                        gl_Position = projectionMatrix * mvPosition;
                        `
                    );
                };

                // Force Update
                mat.needsUpdate = true;
            });
        }
    });
}
