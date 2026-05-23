import { useCallback, useEffect, useRef, useState } from 'react';
import type { SpriteSheet } from '../types';
import { buildSpriteSheet, getTask } from '../services/api';
import { DEMO_MODE } from '../config/demo';

export default function SpriteSheetTool() {
  // ---- form state ----
  const [taskId, setTaskId] = useState('');
  const [assetIds, setAssetIds] = useState<string[]>([]);
  const [animName, setAnimName] = useState('walk_right');
  const [fps, setFps] = useState(12);
  const [frameW, setFrameW] = useState(32);
  const [frameH, setFrameH] = useState(32);
  const [columns, setColumns] = useState(4);

  // ---- result state ----
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<SpriteSheet | null>(null);

  // ---- fetch asset IDs from a completed task ----
  const handleFetchTask = useCallback(async () => {
    if (!taskId.trim()) return;
    setError('');
    setLoading(true);
    try {
      const task = await getTask(taskId.trim());
      if (task.status !== 'ready') {
        setError(`Task is not ready (status: ${task.status})`);
        setLoading(false);
        return;
      }
      const ids = (task.assets || []).map((a) => a.id);
      if (ids.length === 0) {
        setError('Task has no assets');
      } else {
        setAssetIds(ids);
        setError('');
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to fetch task');
    }
    setLoading(false);
  }, [taskId]);

  // ---- build sprite-sheet ----
  const handleBuild = useCallback(async () => {
    if (assetIds.length === 0) return;
    setError('');
    setLoading(true);
    setResult(null);
    try {
      const data = await buildSpriteSheet({
        assetIds,
        animationName: animName,
        frameWidth: frameW,
        frameHeight: frameH,
        fps,
        columns,
      });
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Build failed');
    }
    setLoading(false);
  }, [assetIds, animName, frameW, frameH, fps, columns]);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Sprite Sheet 工具</h2>
        {DEMO_MODE && (
          <span className="text-xs bg-amber-900/60 text-amber-300 border border-amber-700
                           px-2.5 py-1 rounded-full">
            DEMO
          </span>
        )}
      </div>

      {/* ---- step 1: load assets ---- */}
      <section className="card space-y-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          步骤 1 — 加载素材
        </h3>
        <p className="text-xs text-gray-500">
          先在「素材生成」页面生成素材，然后在此输入 task ID 加载素材列表。
        </p>
        <div className="flex gap-2">
          <input
            className="input-field flex-1 font-mono text-sm"
            placeholder="粘贴 task_id..."
            value={taskId}
            onChange={(e) => setTaskId(e.target.value)}
          />
          <button className="btn-secondary text-sm" onClick={handleFetchTask} disabled={loading}>
            加载
          </button>
        </div>
        {assetIds.length > 0 && (
          <div>
            <label className="text-xs text-gray-500">
              已加载 {assetIds.length} 帧（可手动编辑）：
            </label>
            <textarea
              className="input-field h-16 resize-none font-mono text-xs mt-1"
              value={assetIds.join('\n')}
              onChange={(e) =>
                setAssetIds(e.target.value.split('\n').map((s) => s.trim()).filter(Boolean))
              }
            />
          </div>
        )}
      </section>

      {/* ---- step 2: animation settings ---- */}
      <section className="card space-y-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          步骤 2 — 动画设置
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div>
            <label className="text-xs text-gray-400 mb-1 block">动画名</label>
            <input
              className="input-field text-sm"
              value={animName}
              onChange={(e) => setAnimName(e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 mb-1 block">FPS</label>
            <input
              type="number"
              className="input-field text-sm"
              value={fps}
              min={1}
              max={60}
              onChange={(e) => setFps(Number(e.target.value))}
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 mb-1 block">帧宽</label>
            <input
              type="number"
              className="input-field text-sm"
              value={frameW}
              min={8}
              max={512}
              onChange={(e) => setFrameW(Number(e.target.value))}
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 mb-1 block">帧高</label>
            <input
              type="number"
              className="input-field text-sm"
              value={frameH}
              min={8}
              max={512}
              onChange={(e) => setFrameH(Number(e.target.value))}
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 mb-1 block">列数</label>
            <input
              type="number"
              className="input-field text-sm"
              value={columns}
              min={1}
              max={16}
              onChange={(e) => setColumns(Number(e.target.value))}
            />
          </div>
        </div>
        <button
          className="btn-primary w-full py-3 text-base"
          disabled={assetIds.length === 0 || loading}
          onClick={handleBuild}
        >
          {loading ? '生成中...' : '🎞️ 生成 Sprite Sheet'}
        </button>
      </section>

      {/* ---- error ---- */}
      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* ---- result ---- */}
      {result && (
        <>
          {/* spritesheet image + animation preview side by side */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Sprite Sheet image */}
            <section className="card space-y-3">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
                Sprite Sheet ({result.spritesheetSize[0]}×{result.spritesheetSize[1]})
              </h3>
              <div className="bg-[url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAHklEQVQYV2Nk+M9ABYy44v///zMwMDAwMDAwMDAwsDAwAADoFgYF3Y5O+AAAAABJRU5ErkJggg==')] rounded-lg p-2 flex items-center justify-center">
                <img
                  src={result.spritesheetUrl}
                  alt="Sprite Sheet"
                  className="max-w-full pixelated"
                  style={{ imageRendering: 'pixelated' }}
                />
              </div>
              <a
                href={result.spritesheetUrl}
                download
                className="text-xs text-brand-400 hover:text-brand-300 transition-colors"
              >
                下载 PNG
              </a>
            </section>

            {/* animation preview */}
            <section className="card space-y-3">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
                动画预览 — {result.animationName} ({result.fps} fps)
              </h3>
              <AnimationPreview
                spritesheetUrl={result.spritesheetUrl}
                frames={result.frames}
                frameWidth={result.frameWidth}
                frameHeight={result.frameHeight}
                fps={result.fps}
              />
            </section>
          </div>

          {/* frame thumbnails */}
          <section className="card space-y-3">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
              帧列表 ({result.frameCount} 帧)
            </h3>
            <div className="flex gap-2 flex-wrap">
              {result.frames.map((f) => (
                <FrameThumbnail
                  key={f.index}
                  spritesheetUrl={result.spritesheetUrl}
                  frame={f}
                />
              ))}
            </div>
          </section>

          {/* JSON metadata */}
          <section className="card space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
                元数据
              </h3>
              <a
                href={result.metadataUrl}
                target="_blank"
                rel="noreferrer"
                className="text-xs text-brand-400 hover:text-brand-300 transition-colors"
              >
                下载 JSON
              </a>
            </div>
            <pre className="bg-gray-950 border border-gray-800 rounded-lg p-4
                            text-xs text-green-400/90 font-mono leading-relaxed
                            overflow-x-auto max-h-64 overflow-y-auto">
{JSON.stringify(
  {
    animation_name: result.animationName,
    frame_width: result.frameWidth,
    frame_height: result.frameHeight,
    frame_count: result.frameCount,
    fps: result.fps,
    spritesheet_size: result.spritesheetSize,
    frames: result.frames,
  },
  null,
  2,
)}
            </pre>
          </section>
        </>
      )}

      {/* empty state */}
      {!result && !loading && !error && (
        <section className="card text-center py-12">
          <p className="text-gray-600">加载素材并设置参数后，点击生成按钮</p>
          <p className="text-xs text-gray-700 mt-1">
            生成的 Sprite Sheet 和动画预览将显示在此处
          </p>
        </section>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function AnimationPreview({
  spritesheetUrl,
  frames,
  frameWidth,
  frameHeight,
  fps,
}: {
  spritesheetUrl: string;
  frames: { index: number; x: number; y: number; width: number; height: number }[];
  frameWidth: number;
  frameHeight: number;
  fps: number;
}) {
  const [frameIdx, setFrameIdx] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [paused, setPaused] = useState(false);

  const frame = frames[frameIdx] || frames[0];

  useEffect(() => {
    if (paused || frames.length <= 1) return;
    const interval = 1000 / Math.max(1, fps);
    timerRef.current = setInterval(() => {
      setFrameIdx((prev) => (prev + 1) % frames.length);
    }, interval);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [fps, frames.length, paused]);

  const displayW = Math.min(frameWidth, 128);
  const displayH = Math.min(frameHeight, 128);
  const scale = Math.min(displayW / frameWidth, displayH / frameHeight);

  return (
    <div className="flex flex-col items-center gap-3">
      <div
        className="border border-gray-700 rounded-lg bg-[url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAHklEQVQYV2Nk+M9ABYy44v///zMwMDAwMDAwMDAwsDAwAADoFgYF3Y5O+AAAAABJRU5ErkJggg==')] overflow-hidden"
        style={{
          width: displayW,
          height: displayH,
        }}
      >
        <div
          style={{
            width: displayW,
            height: displayH,
            backgroundImage: `url(${spritesheetUrl})`,
            backgroundSize: `${frameWidth * scale}px ${frameHeight * scale}px`,
            backgroundPosition: `-${frame.x * scale}px -${frame.y * scale}px`,
            imageRendering: 'pixelated',
            backgroundRepeat: 'no-repeat',
          }}
        />
      </div>

      {/* controls */}
      <div className="flex items-center gap-3 text-xs">
        <button
          className="btn-secondary text-xs py-1 px-3"
          onClick={() => setPaused(!paused)}
        >
          {paused ? '▶ 播放' : '⏸ 暂停'}
        </button>
        <button
          className="btn-secondary text-xs py-1 px-3"
          onClick={() => setFrameIdx((prev) => (prev - 1 + frames.length) % frames.length)}
        >
          ◀
        </button>
        <span className="text-gray-400 font-mono">
          {frameIdx + 1} / {frames.length}
        </span>
        <button
          className="btn-secondary text-xs py-1 px-3"
          onClick={() => setFrameIdx((prev) => (prev + 1) % frames.length)}
        >
          ▶
        </button>
        <span className="text-gray-600">
          {fps} fps · {frameWidth}×{frameHeight}px
        </span>
      </div>
    </div>
  );
}

function FrameThumbnail({
  spritesheetUrl,
  frame,
}: {
  spritesheetUrl: string;
  frame: { index: number; x: number; y: number; width: number; height: number };
}) {
  const thumbScale = Math.min(1, 64 / Math.max(frame.width, frame.height));
  const tw = Math.round(frame.width * thumbScale);
  const th = Math.round(frame.height * thumbScale);
  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className="border border-gray-700 rounded bg-[url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAHklEQVQYV2Nk+M9ABYy44v///zMwMDAwMDAwMDAwsDAwAADoFgYF3Y5O+AAAAABJRU5ErkJggg==')] overflow-hidden"
        style={{ width: tw, height: th }}
      >
        <div
          style={{
            width: tw,
            height: th,
            backgroundImage: `url(${spritesheetUrl})`,
            backgroundSize: `${frame.width * thumbScale}px ${frame.height * thumbScale}px`,
            backgroundPosition: `-${frame.x * thumbScale}px -${frame.y * thumbScale}px`,
            imageRendering: 'pixelated',
          }}
        />
      </div>
      <span className="text-[10px] text-gray-600 font-mono">#{frame.index}</span>
    </div>
  );
}
