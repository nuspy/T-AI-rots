"use client";

/* Il cielo dietro il tavolo: stelle in parallasse e una nebulosa che respira.
 *
 * three.js si importa solo nel browser e solo dopo il montaggio: pesa, e la
 * pagina deve apparire prima del cielo. Con `prefers-reduced-motion` il cielo
 * si disegna una volta e resta fermo; quando la scheda non è visibile il
 * ciclo si sospende, così non consuma batteria per nessuno.
 */

import { useEffect, useRef } from "react";
import stili from "./cosmo.module.css";

const VERTICE = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = vec4(position, 1.0);
  }
`;

/* Una nebulosa di rumore frattale: viola e oro su nero, lentissima. */
const FRAMMENTO = /* glsl */ `
  precision highp float;
  varying vec2 vUv;
  uniform float uTempo;
  uniform vec2 uMouse;
  uniform vec2 uRisoluzione;

  float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float rumore(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
  }
  float fbm(vec2 p) {
    float v = 0.0, a = 0.5;
    for (int i = 0; i < 5; i++) { v += a * rumore(p); p *= 2.02; a *= 0.5; }
    return v;
  }
  void main() {
    vec2 uv = vUv;
    uv.x *= uRisoluzione.x / uRisoluzione.y;
    vec2 p = uv * 2.2 + uMouse * 0.08;
    float t = uTempo * 0.018;
    float n = fbm(p + vec2(t, -t * 0.6) + fbm(p * 0.7 - t));
    float m = fbm(p * 1.6 - vec2(t * 0.8, t));
    vec3 viola = vec3(0.36, 0.2, 0.66);
    vec3 indaco = vec3(0.09, 0.07, 0.24);
    vec3 oro = vec3(0.72, 0.53, 0.2);
    vec3 col = mix(vec3(0.02, 0.015, 0.05), indaco, smoothstep(0.2, 0.8, n));
    col = mix(col, viola, smoothstep(0.5, 0.9, n) * 0.7);
    col += oro * pow(smoothstep(0.55, 1.0, m), 2.5) * 0.3;
    float vignetta = smoothstep(1.25, 0.25, length(vUv - 0.5) * 1.6);
    gl_FragColor = vec4(col * vignetta, 1.0);
  }
`;

export function Cosmo() {
  const tela = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    let fermo = false;
    let pulizia: (() => void) | undefined;
    const meno = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    (async () => {
      const THREE = await import("three");
      const canvas = tela.current;
      if (!canvas || fermo) return;

      let renderer: import("three").WebGLRenderer;
      try {
        renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false, powerPreference: "low-power" });
      } catch {
        /* Niente WebGL: resta il gradiente del CSS. */
        return;
      }
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));

      const scena = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 100);
      camera.position.z = 5;

      /* La nebulosa: un quadrato che copre lo schermo, disegnato per primo. */
      const uniformi = {
        uTempo: { value: 0 },
        uMouse: { value: new THREE.Vector2() },
        uRisoluzione: { value: new THREE.Vector2(1, 1) },
      };
      const nebulosa = new THREE.Mesh(
        new THREE.PlaneGeometry(2, 2),
        new THREE.ShaderMaterial({
          vertexShader: VERTICE,
          fragmentShader: FRAMMENTO,
          uniforms: uniformi,
          depthWrite: false,
          depthTest: false,
        }),
      );
      nebulosa.frustumCulled = false;
      nebulosa.renderOrder = -1;
      scena.add(nebulosa);

      /* Tre strati di stelle a distanze diverse: la parallasse viene da sé. */
      const strati: import("three").Points[] = [];
      const quante = window.innerWidth < 700 ? 500 : 1100;
      [0.9, 1.6, 2.6].forEach((dimensione, i) => {
        const pos = new Float32Array(quante * 3);
        for (let k = 0; k < quante; k++) {
          pos[k * 3] = (Math.random() - 0.5) * 30;
          pos[k * 3 + 1] = (Math.random() - 0.5) * 18;
          pos[k * 3 + 2] = -Math.random() * 20 - i * 4;
        }
        const geo = new THREE.BufferGeometry();
        geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
        const punti = new THREE.Points(
          geo,
          new THREE.PointsMaterial({
            size: dimensione * 0.035,
            color: i === 2 ? 0xf1d68e : 0xe8e0ff,
            transparent: true,
            opacity: 0.55 + i * 0.12,
            depthWrite: false,
          }),
        );
        strati.push(punti);
        scena.add(punti);
      });

      const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
      const muovi = (e: PointerEvent) => {
        mouse.tx = (e.clientX / window.innerWidth - 0.5) * 2;
        mouse.ty = (e.clientY / window.innerHeight - 0.5) * 2;
      };
      window.addEventListener("pointermove", muovi, { passive: true });

      const ridimensiona = () => {
        const w = window.innerWidth;
        const h = window.innerHeight;
        renderer.setSize(w, h, false);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        uniformi.uRisoluzione.value.set(w, h);
      };
      ridimensiona();
      window.addEventListener("resize", ridimensiona);

      const orologio = new THREE.Clock();
      let ciclo = 0;
      const disegna = () => {
        const t = orologio.getElapsedTime();
        mouse.x += (mouse.tx - mouse.x) * 0.03;
        mouse.y += (mouse.ty - mouse.y) * 0.03;
        uniformi.uTempo.value = t;
        uniformi.uMouse.value.set(mouse.x, mouse.y);
        strati.forEach((s, i) => {
          s.rotation.z = t * 0.004 * (i + 1);
          s.position.x = -mouse.x * 0.25 * (i + 1);
          s.position.y = mouse.y * 0.18 * (i + 1);
        });
        renderer.render(scena, camera);
        if (!meno && !document.hidden) ciclo = requestAnimationFrame(disegna);
      };
      const visibilita = () => {
        cancelAnimationFrame(ciclo);
        if (!document.hidden && !meno) ciclo = requestAnimationFrame(disegna);
      };
      document.addEventListener("visibilitychange", visibilita);
      disegna();

      pulizia = () => {
        cancelAnimationFrame(ciclo);
        window.removeEventListener("pointermove", muovi);
        window.removeEventListener("resize", ridimensiona);
        document.removeEventListener("visibilitychange", visibilita);
        renderer.dispose();
      };
    })();

    return () => {
      fermo = true;
      pulizia?.();
    };
  }, []);

  return <canvas ref={tela} className={stili.cosmo} aria-hidden="true" />;
}
