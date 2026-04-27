import { motion } from 'framer-motion'
import { FiCheckCircle, FiAlertTriangle, FiClock, FiCpu, FiVideo, FiTag, FiInfo } from 'react-icons/fi'

function ModelBar({ model, fakeProb, realProb, specialty, isFake, index }) {
  const barColor = fakeProb >= realProb ? '#ef4444' : '#22c55e'
  const dominantPct = Math.max(fakeProb, realProb)
  const dominant = fakeProb >= realProb ? 'FAKE' : 'REAL'

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.5 + index * 0.08 }}
      style={{
        background: 'rgba(255,255,255,0.02)',
        border: '1px solid rgba(255,255,255,0.05)',
        borderRadius: 10, padding: '10px 12px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
        <div>
          <p style={{ fontSize: 11, fontWeight: 700, color: '#e5e7eb', letterSpacing: '0.02em' }}>
            {model}
          </p>
          <p style={{ fontSize: 10, color: '#6b7280', marginTop: 1 }}>{specialty}</p>
        </div>
        <span style={{
          fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 20,
          background: fakeProb >= realProb ? 'rgba(239,68,68,0.15)' : 'rgba(34,197,94,0.15)',
          color: fakeProb >= realProb ? '#f87171' : '#4ade80',
          border: `1px solid ${fakeProb >= realProb ? 'rgba(239,68,68,0.25)' : 'rgba(34,197,94,0.25)'}`,
        }}>
          {dominant} {dominantPct.toFixed(0)}%
        </span>
      </div>
      {/* Bar */}
      <div style={{ height: 4, borderRadius: 4, background: 'rgba(255,255,255,0.05)', overflow: 'hidden' }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${fakeProb}%` }}
          transition={{ delay: 0.6 + index * 0.08, duration: 0.6, ease: 'easeOut' }}
          style={{ height: '100%', borderRadius: 4, background: '#ef4444' }}
        />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
        <span style={{ fontSize: 9, color: '#6b7280' }}>Real {realProb.toFixed(0)}%</span>
        <span style={{ fontSize: 9, color: '#6b7280' }}>Fake {fakeProb.toFixed(0)}%</span>
      </div>
    </motion.div>
  )
}

function ResultsDisplay({ result, loading }) {
  if (loading) {
    return (
      <div className="relative flex items-center justify-center h-full min-h-[300px] rounded-2xl border border-white/5 bg-[#0a0a1a]/60 backdrop-blur-xl overflow-hidden">
        {[80, 120, 160].map((size, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full border border-blue-500/20"
            style={{ width: size, height: size }}
            animate={{ rotate: i % 2 === 0 ? 360 : -360, scale: [1, 1.05, 1] }}
            transition={{ duration: 3 + i, repeat: Infinity, ease: 'linear' }}
          />
        ))}
        <div className="text-center relative z-10">
          <motion.div
            className="w-16 h-16 mx-auto mb-4 rounded-full border-2 border-blue-500/30 border-t-blue-400"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
          <p className="text-lg font-semibold text-gray-200">Analyzing Media</p>
          <p className="text-sm text-gray-500 mt-1">AI Detection in Progress...</p>
        </div>
      </div>
    )
  }

  if (!result) return null

  const isFake = result.prediction === 'FAKE'
  const isUncertain = result.prediction_state === 'UNCERTAIN'
  const Icon = isFake ? FiAlertTriangle : FiCheckCircle
  const accentColor = isFake ? '#ef4444' : '#22c55e'
  const glowColor   = isFake ? 'rgba(239,68,68,0.3)' : 'rgba(34,197,94,0.3)'

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      style={{
        position: 'relative', borderRadius: 16,
        border: `1px solid ${accentColor}33`,
        background: 'rgba(10,10,26,0.85)', backdropFilter: 'blur(20px)',
        overflow: 'hidden', display: 'flex', flexDirection: 'column',
        height: '100%',
      }}
    >
      {/* Ambient glow */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: `radial-gradient(ellipse at 50% 0%, ${glowColor} 0%, transparent 65%)`,
      }} />

      {/* Animated top border */}
      <motion.div
        style={{
          position: 'absolute', top: 0, left: 0, height: 2, width: '50%',
          background: `linear-gradient(90deg, transparent, ${accentColor}, transparent)`,
        }}
        animate={{ x: ['-100%', '200%'] }}
        transition={{ duration: 2.5, repeat: Infinity, ease: 'linear' }}
      />

      <div style={{ position: 'relative', zIndex: 1, overflowY: 'auto', padding: '24px 20px', display: 'flex', flexDirection: 'column', gap: 16 }}>

        {/* ── Verdict ── */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingBottom: 4 }}>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', duration: 0.6 }}
            style={{ position: 'relative', marginBottom: 14 }}
          >
            <motion.div
              style={{ position: 'absolute', inset: 0, borderRadius: '50%', background: glowColor }}
              animate={{ scale: [1, 1.8, 1], opacity: [0.6, 0, 0.6] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
            />
            <div style={{
              position: 'relative', width: 96, height: 96, borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              border: `2px solid ${accentColor}`,
              background: `radial-gradient(circle, ${glowColor} 0%, transparent 70%)`,
              boxShadow: `0 0 30px ${glowColor}`,
            }}>
              <Icon style={{ color: accentColor, fontSize: '2.5rem' }} />
            </div>
          </motion.div>

          <motion.h2
            style={{
              fontSize: 52, fontWeight: 900, letterSpacing: '0.12em', margin: 0,
              color: accentColor,
              textShadow: `0 0 20px ${glowColor}, 0 0 40px ${glowColor}`,
            }}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.25 }}
          >
            {result.prediction}
          </motion.h2>

          {isUncertain && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              style={{
                marginTop: 12,
                padding: '8px 12px',
                borderRadius: 999,
                border: '1px solid rgba(245,158,11,0.35)',
                background: 'rgba(245,158,11,0.10)',
                color: '#fbbf24',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                fontSize: 12,
                fontWeight: 700,
              }}
            >
              <FiAlertTriangle style={{ fontSize: 12 }} />
              Mixed Signals
              {typeof result.disagreement_score === 'number' && (
                <span style={{ color: '#fde68a', fontWeight: 600 }}>
                  {result.disagreement_score.toFixed(0)}%
                </span>
              )}
            </motion.div>
          )}
        </div>

        {/* ── Fake type badge + detail ── */}
        {isFake && result.fake_type && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            style={{
              borderRadius: 12,
              border: '1px solid rgba(239,68,68,0.2)',
              background: 'rgba(239,68,68,0.06)',
              padding: '12px 14px',
            }}
          >
            {/* Type label */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <FiTag style={{ color: '#f87171', fontSize: 13, flexShrink: 0 }} />
              <span style={{ fontSize: 13, fontWeight: 700, color: '#fca5a5', letterSpacing: '0.03em' }}>
                {result.fake_type}
              </span>
            </div>
            {/* Tags */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
              {(result.fake_tags || []).map(tag => (
                <span key={tag} style={{
                  fontSize: 10, fontWeight: 600, padding: '2px 9px', borderRadius: 20,
                  background: 'rgba(239,68,68,0.12)',
                  color: '#fca5a5',
                  border: '1px solid rgba(239,68,68,0.2)',
                  letterSpacing: '0.05em',
                }}>
                  {tag}
                </span>
              ))}
            </div>
            {/* Detail */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 7 }}>
              <FiInfo style={{ color: '#9ca3af', fontSize: 11, marginTop: 2, flexShrink: 0 }} />
              <p style={{ fontSize: 11, color: '#9ca3af', lineHeight: 1.6, margin: 0 }}>
                {result.fake_type_detail}
              </p>
            </div>
          </motion.div>
        )}

        {/* ── Real image description ── */}
        {!isFake && !isUncertain && (
          <motion.p
            style={{ fontSize: 13, color: '#6b7280', textAlign: 'center', margin: 0 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {`This ${result.frames_analyzed ? 'video' : 'image'} appears to be authentic`}
          </motion.p>
        )}

        {isUncertain && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            style={{
              borderRadius: 12,
              border: '1px solid rgba(245,158,11,0.18)',
              background: 'rgba(245,158,11,0.06)',
              padding: '12px 14px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <FiInfo style={{ color: '#fbbf24', fontSize: 13, flexShrink: 0 }} />
              <span style={{ fontSize: 13, fontWeight: 700, color: '#fde68a' }}>
                Ensemble disagreement detected
              </span>
            </div>
            <p style={{ fontSize: 11, color: '#d1d5db', lineHeight: 1.6, margin: 0 }}>
              The model verdict is preserved for compatibility, but the vote split or confidence spread
              suggests this result should be treated as uncertain.
            </p>
            {Array.isArray(result.uncertain_reason) && result.uncertain_reason.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 10 }}>
                {result.uncertain_reason.map(reason => (
                  <span
                    key={reason}
                    style={{
                      fontSize: 10,
                      padding: '3px 8px',
                      borderRadius: 999,
                      background: 'rgba(245,158,11,0.12)',
                      color: '#fde68a',
                      border: '1px solid rgba(245,158,11,0.18)',
                    }}
                  >
                    {reason}
                  </span>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* ── Per-model breakdown ── */}
        {result.per_model && result.per_model.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <p style={{
              fontSize: 10, fontWeight: 700, color: '#6b7280',
              letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 8,
            }}>
              Model Breakdown
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {result.per_model.map((m, i) => (
                <ModelBar
                  key={m.model}
                  model={m.model}
                  fakeProb={m.fake_prob}
                  realProb={m.real_prob}
                  specialty={m.specialty}
                  isFake={isFake}
                  index={i}
                />
              ))}
            </div>
          </motion.div>
        )}

        {/* ── Video details ── */}
        {result.frames_analyzed && (
          <motion.div
            style={{
              borderRadius: 12, border: '1px solid rgba(255,255,255,0.05)',
              background: 'rgba(255,255,255,0.02)', padding: '12px 14px',
            }}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.55 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
              <FiVideo style={{ color: '#a78bfa', fontSize: 13 }} />
              <span style={{ fontSize: 12, fontWeight: 600, color: '#d1d5db' }}>Video Analysis</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              {[
                { label: 'Frames Analyzed', value: result.frames_analyzed, color: '#60a5fa' },
                { label: 'Method', value: result.aggregation_method?.replace('_', ' '), color: '#a78bfa' },
                ...(result.fake_frames !== undefined ? [
                  { label: 'Fake Frames', value: result.fake_frames, color: '#f87171' },
                  { label: 'Real Frames', value: result.real_frames, color: '#4ade80' },
                ] : []),
              ].map(({ label, value, color }) => (
                <div key={label} style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 8, padding: '8px 10px', textAlign: 'center' }}>
                  <p style={{ fontSize: 10, color: '#6b7280', marginBottom: 3 }}>{label}</p>
                  <p style={{ fontSize: 13, fontWeight: 700, color }}>{value}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── Meta row ── */}
        <motion.div
          style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          {[
            { Icon: FiClock, label: 'Processing Time', value: `${result.total_processing_time ?? result.inference_time}s`, color: '#60a5fa' },
            { Icon: FiCpu,   label: 'Device',          value: result.device || 'CPU',                                     color: '#a78bfa' },
          ].map(({ Icon: MetaIcon, label, value, color }) => (
            <div key={label} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)',
              borderRadius: 12, padding: '10px 12px',
            }}>
              <MetaIcon style={{ color, fontSize: 16, flexShrink: 0 }} />
              <div>
                <p style={{ fontSize: 10, color: '#6b7280', marginBottom: 2 }}>{label}</p>
                <p style={{ fontSize: 12, fontWeight: 600, color: '#e5e7eb' }}>{value}</p>
              </div>
            </div>
          ))}
        </motion.div>

      </div>
    </motion.div>
  )
}

export default ResultsDisplay
