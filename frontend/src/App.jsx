import { useState, useEffect, useRef } from 'react'
import { Toaster } from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'
import Header from './components/Header'
import ImageUpload from './components/ImageUpload'
import ResultsDisplay from './components/ResultsDisplay'
import Statistics from './components/Statistics'
import History from './components/History'
import { FiUpload, FiBarChart2, FiClock } from 'react-icons/fi'

/* ─── static data outside component ─── */
const ORBS = [
  { size: 600, x: '-8%',  y: '-20%', color: 'rgba(59,130,246,0.10)', dur: 18 },
  { size: 450, x: '68%',  y: '55%',  color: 'rgba(139,92,246,0.09)', dur: 22 },
  { size: 320, x: '82%',  y: '-8%',  color: 'rgba(236,72,153,0.07)', dur: 15 },
  { size: 260, x: '18%',  y: '70%',  color: 'rgba(59,130,246,0.06)', dur: 20 },
]
const PARTICLES = Array.from({ length: 20 }, (_, i) => ({
  id: i,
  x: `${Math.random() * 100}%`,
  y: `${Math.random() * 100}%`,
  size: Math.random() * 2.5 + 1,
  dur: Math.random() * 8 + 6,
  delay: Math.random() * 5,
}))
const TABS = [
  { id: 'upload',  label: 'Analyze',    Icon: FiUpload    },
  { id: 'stats',   label: 'Statistics', Icon: FiBarChart2 },
  { id: 'history', label: 'History',    Icon: FiClock     },
]

export default function App() {
  const [activeTab,   setActiveTab]   = useState('upload')
  const [result,      setResult]      = useState(null)
  const [loading,     setLoading]     = useState(false)
  const [statistics,  setStatistics]  = useState(null)
  const analyzeRef = useRef(null)   // shared ref: exposes {analyze, open, hasFile} from ImageUpload

  useEffect(() => {
    fetch('/api/v1/statistics')
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setStatistics(d))
      .catch(() => {})
  }, [result])

  return (
    <>
      {/* ── Fixed ambient layer — lives outside layout ── */}
      <div style={{ position:'fixed', inset:0, zIndex:0, pointerEvents:'none', overflow:'hidden' }}>
        {ORBS.map((o, i) => (
          <motion.div key={i}
            style={{
              position: 'absolute',
              width: o.size, height: o.size,
              left: o.x, top: o.y,
              background: `radial-gradient(circle, ${o.color} 0%, transparent 70%)`,
              filter: 'blur(70px)',
              borderRadius: '50%',
            }}
            animate={{ x:[0,35,-25,15,0], y:[0,-25,35,-15,0], scale:[1,1.08,.96,1.04,1] }}
            transition={{ duration: o.dur, repeat: Infinity, ease: 'easeInOut' }}
          />
        ))}
        {PARTICLES.map(p => (
          <motion.div key={p.id}
            style={{
              position: 'absolute',
              width: p.size, height: p.size,
              left: p.x, top: p.y,
              borderRadius: '50%',
              background: 'rgba(139,92,246,0.7)',
              boxShadow: '0 0 4px rgba(139,92,246,0.9)',
            }}
            animate={{ y:[0,-28,0], opacity:[0.15,0.7,0.15] }}
            transition={{ duration: p.dur, delay: p.delay, repeat: Infinity, ease: 'easeInOut' }}
          />
        ))}
        {/* grid */}
        <div style={{
          position:'absolute', inset:0, opacity:0.025,
          backgroundImage: `linear-gradient(rgba(59,130,246,1) 1px,transparent 1px),linear-gradient(90deg,rgba(59,130,246,1) 1px,transparent 1px)`,
          backgroundSize: '60px 60px',
        }} />
      </div>

      {/* ── App shell — full height flex column ── */}
      <div style={{ position:'relative', zIndex:1, height:'100%', display:'flex', flexDirection:'column' }}>

        <Toaster position="top-right" toastOptions={{
          style: { background:'rgba(10,10,25,0.95)', color:'#e2e8f0',
            border:'1px solid rgba(59,130,246,0.25)', backdropFilter:'blur(20px)' }
        }} />

        {/* Header */}
        <div style={{ flexShrink: 0 }}>
          <Header />
        </div>

        {/* Tabs */}
        <div style={{ flexShrink:0, display:'flex', justifyContent:'center', padding:'12px 16px' }}>
          <div style={{
            display:'inline-flex', gap:4,
            background:'rgba(13,13,31,0.9)', border:'1px solid rgba(255,255,255,0.06)',
            borderRadius:16, padding:6, backdropFilter:'blur(20px)',
          }}>
            {TABS.map(({ id, label, Icon }) => {
              const active = activeTab === id
              return (
                <button key={id} onClick={() => setActiveTab(id)}
                  style={{
                    position:'relative', display:'inline-flex', alignItems:'center', gap:8,
                    padding:'8px 24px', borderRadius:12, border:'none', cursor:'pointer',
                    fontSize:14, fontWeight:600,
                    background: active ? 'linear-gradient(135deg,#2563eb,#7c3aed)' : 'transparent',
                    color: active ? '#fff' : '#6b7280',
                    transition: 'all 0.2s',
                    boxShadow: active ? '0 4px 20px rgba(37,99,235,0.3)' : 'none',
                  }}
                >
                  <Icon style={{ fontSize:14 }} />
                  {label}
                </button>
              )
            })}
          </div>
        </div>

        {/* Content — takes all remaining height */}
        <div style={{ flex:1, minHeight:0, padding:'0 16px 16px', overflow:'hidden' }}>
          <AnimatePresence mode="wait">

            {activeTab === 'upload' && (
              <motion.div key="upload"
                style={{ height:'100%', display:'grid', gridTemplateColumns:'1fr 1fr', gap:16 }}
                initial={{ opacity:0, y:16 }} animate={{ opacity:1, y:0 }}
                exit={{ opacity:0, y:-16 }} transition={{ duration:0.3 }}
              >
                <div style={{ minHeight:0, overflowY:'auto' }}>
                  <ImageUpload setResult={setResult} loading={loading} setLoading={setLoading} analyzeRef={analyzeRef} />
                </div>
                <div style={{ minHeight:0, overflowY:'auto' }}>
                  <AnimatePresence mode="wait">
                    {(result || loading)
                      ? <ResultsDisplay key="res" result={result} loading={loading} />
                      : <IdlePlaceholder key="idle" analyzeRef={analyzeRef} />
                    }
                  </AnimatePresence>
                </div>
              </motion.div>
            )}

            {activeTab === 'stats' && (
              <motion.div key="stats"
                style={{ height:'100%', overflowY:'auto' }}
                initial={{ opacity:0, y:16 }} animate={{ opacity:1, y:0 }}
                exit={{ opacity:0, y:-16 }} transition={{ duration:0.3 }}
              >
                <Statistics statistics={statistics} />
              </motion.div>
            )}

            {activeTab === 'history' && (
              <motion.div key="history"
                style={{ height:'100%', overflowY:'auto' }}
                initial={{ opacity:0, y:16 }} animate={{ opacity:1, y:0 }}
                exit={{ opacity:0, y:-16 }} transition={{ duration:0.3 }}
              >
                <History />
              </motion.div>
            )}

          </AnimatePresence>
        </div>

        {/* Watermark */}
        <div style={{
          flexShrink: 0, textAlign: 'center', padding: '6px 0 8px',
          borderTop: '1px solid rgba(255,255,255,0.04)',
        }}>
          <span style={{ fontSize: 11, color: '#374151', letterSpacing: '0.08em' }}>
            Developed by{' '}
            <span style={{
              background: 'linear-gradient(90deg,#60a5fa,#a78bfa)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
              fontWeight: 700,
            }}>
              tanaytejush
            </span>
          </span>
        </div>

      </div>
    </>
  )
}

function IdlePlaceholder({ analyzeRef }) {
  const handleClick = () => {
    const ctrl = analyzeRef?.current
    if (!ctrl) return
    if (ctrl.hasFile) ctrl.analyze()   // file selected → run analysis
    else ctrl.open()                    // no file → open picker
  }

  return (
    <motion.div
      onClick={handleClick}
      initial={{ opacity:0 }} animate={{ opacity:1 }} exit={{ opacity:0 }}
      style={{
        height:'100%', minHeight:280, cursor:'pointer',
        display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
        borderRadius:16, border:'1px solid rgba(255,255,255,0.05)',
        background:'rgba(10,10,26,0.5)', backdropFilter:'blur(16px)',
        position:'relative', overflow:'hidden',
        transition:'border-color 0.2s, background 0.2s',
      }}
      whileHover={{ borderColor:'rgba(59,130,246,0.25)', backgroundColor:'rgba(15,15,35,0.6)' }}
    >
      {/* corner brackets */}
      {[{t:16,l:16,bt:'2px 0 0 2px'},{t:16,r:16,bt:'2px 2px 0 0'},
        {b:16,l:16,bt:'0 0 2px 2px'},{b:16,r:16,bt:'0 2px 2px 0'}].map((s,i) => (
        <div key={i} style={{
          position:'absolute', width:24, height:24,
          top:s.t, left:s.l, bottom:s.b, right:s.r,
          border:'1px solid rgba(59,130,246,0.25)',
          borderRadius: s.bt,
        }} />
      ))}

      {/* pulsing rings */}
      {[100,140,180].map((sz,i) => (
        <motion.div key={i} style={{
          position:'absolute', width:sz, height:sz,
          border:'1px solid rgba(59,130,246,0.08)', borderRadius:'50%',
        }}
          animate={{ scale:[1,1.12,1], opacity:[0.5,0.1,0.5] }}
          transition={{ duration:3+i*0.7, repeat:Infinity, ease:'easeInOut', delay:i*0.4 }}
        />
      ))}

      <div style={{ position:'relative', zIndex:1, textAlign:'center', padding:'0 32px' }}>
        <div style={{
          width:56, height:56, margin:'0 auto 20px',
          borderRadius:14, display:'flex', alignItems:'center', justifyContent:'center',
          background:'linear-gradient(135deg,rgba(37,99,235,0.15),rgba(124,58,237,0.15))',
          border:'1px solid rgba(59,130,246,0.2)',
        }}>
          <FiUpload style={{ fontSize:24, color:'#60a5fa' }} />
        </div>
        <p style={{ fontSize:15, fontWeight:600, color:'#d1d5db', marginBottom:6 }}>
          Click to Analyze
        </p>
        <p style={{ fontSize:13, color:'#4b5563' }}>
          Select a file on the left, then click here to run
        </p>
        <div style={{ marginTop:20, display:'flex', alignItems:'center', justifyContent:'center', gap:10 }}>
          <div style={{ height:1, width:48, background:'linear-gradient(to right, transparent, rgba(59,130,246,0.3))' }} />
          <span style={{ fontSize:11, color:'#374151', letterSpacing:'0.1em', textTransform:'uppercase' }}>3 AI Models</span>
          <div style={{ height:1, width:48, background:'linear-gradient(to left, transparent, rgba(59,130,246,0.3))' }} />
        </div>
      </div>
    </motion.div>
  )
}
