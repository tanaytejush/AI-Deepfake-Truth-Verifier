import { FiShield } from 'react-icons/fi'
import { motion } from 'framer-motion'

export default function Header() {
  return (
    <header style={{
      position:'sticky', top:0, zIndex:50,
      background:'rgba(5,5,15,0.85)', backdropFilter:'blur(24px)',
      borderBottom:'1px solid rgba(255,255,255,0.05)',
      padding:'12px 24px',
    }}>
      {/* Scan line */}
      <motion.div
        style={{ position:'absolute', top:0, left:0, height:2, width:'40%',
          background:'linear-gradient(90deg,transparent,#3b82f6,transparent)', pointerEvents:'none' }}
        animate={{ x:['-100%','250%'] }}
        transition={{ duration:3, repeat:Infinity, ease:'linear' }}
      />

      <div style={{ maxWidth:1200, margin:'0 auto', display:'flex',
        alignItems:'center', justifyContent:'space-between' }}>

        {/* Left spacer */}
        <div style={{ width:160 }} />

        {/* Center */}
        <div style={{ display:'flex', alignItems:'center', gap:12 }}>
          <div style={{ position:'relative', flexShrink:0 }}>
            <motion.div style={{ position:'absolute', inset:0, borderRadius:12,
              background:'rgba(59,130,246,0.3)' }}
              animate={{ scale:[1,1.6,1], opacity:[0.6,0,0.6] }}
              transition={{ duration:2.5, repeat:Infinity, ease:'easeOut' }}
            />
            <div style={{ position:'relative', background:'linear-gradient(135deg,#2563eb,#7c3aed)',
              padding:10, borderRadius:12, boxShadow:'0 4px 20px rgba(37,99,235,0.4)',
              display:'flex', alignItems:'center', justifyContent:'center' }}>
              <FiShield style={{ color:'#fff', fontSize:20 }} />
            </div>
          </div>
          <div>
            <h1 style={{ margin:0, fontSize:22, fontWeight:800, letterSpacing:'-0.02em',
              background:'linear-gradient(90deg,#60a5fa,#a78bfa,#f472b6)',
              WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent',
              backgroundClip:'text' }}>
              AI-based Image Authenticity Verification System
            </h1>
            <p style={{ margin:0, fontSize:11, color:'#4b5563',
              letterSpacing:'0.12em', textTransform:'uppercase' }}>
              Vision Transformer · Real-time Detection
            </p>
          </div>
        </div>

        {/* Right: status */}
        <div style={{ width:160, display:'flex', justifyContent:'flex-end' }}>
          <div style={{ display:'flex', alignItems:'center', gap:8,
            background:'rgba(13,13,31,0.8)', border:'1px solid rgba(34,197,94,0.15)',
            padding:'6px 14px', borderRadius:20 }}>
            <motion.div style={{ width:7, height:7, borderRadius:'50%', background:'#4ade80' }}
              animate={{ opacity:[1,0.3,1] }}
              transition={{ duration:1.5, repeat:Infinity }}
            />
            <span style={{ fontSize:11, color:'#4ade80', fontWeight:500 }}>Model Online</span>
          </div>
        </div>

      </div>
    </header>
  )
}
