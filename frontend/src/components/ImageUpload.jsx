import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { FiUpload, FiImage, FiZap, FiVideo, FiX } from 'react-icons/fi'
import toast from 'react-hot-toast'
import axios from 'axios'

const Corner = ({ style }) => (
  <div style={{ position:'absolute', width:24, height:24,
    border:'1.5px solid rgba(59,130,246,0.4)', ...style }} />
)

export default function ImageUpload({ setResult, loading, setLoading, analyzeRef }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview]           = useState(null)
  const [fileType, setFileType]         = useState(null)

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return
    const type = file.type.startsWith('video/') ? 'video' : 'image'
    const maxSize = type === 'video' ? 50 * 1024 * 1024 : 10 * 1024 * 1024
    if (file.size > maxSize) {
      toast.error(`File too large. Max ${type === 'video' ? '50MB' : '10MB'}`)
      return
    }
    setFileType(type)
    setSelectedFile(file)
    const reader = new FileReader()
    reader.onload = () => setPreview(reader.result)
    reader.readAsDataURL(file)
    toast.success(`${type === 'video' ? 'Video' : 'Image'} loaded!`)
  }, [])

  const { getRootProps, getInputProps, open } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpeg','.jpg','.png'], 'video/*': ['.mp4','.avi','.mov','.mkv'] },
    multiple: false,
    noClick: !!preview,   // disable click-to-open when already has a file
  })

  const handleAnalyze = async () => {
    if (!selectedFile) return
    setLoading(true)
    setResult(null)
    const formData = new FormData()
    formData.append('file', selectedFile)
    const endpoint = fileType === 'video' ? '/api/v1/predict/video' : '/api/v1/predict'
    try {
      const res = await axios.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(res.data)
      toast.success('Analysis complete!')
    } catch (err) {
      if (!err.response) {
        toast.error('Backend offline — run: uvicorn app.main:app --port 8001')
      } else {
        const requestId = err.response?.headers?.['x-request-id']
        const detail = err.response?.data?.detail || 'Analysis failed'
        toast.error(requestId ? `${detail} (Req: ${requestId})` : detail)
      }
    } finally {
      setLoading(false)
    }
  }

  // Expose handleAnalyze and open to parent via ref
  if (analyzeRef) {
    analyzeRef.current = { analyze: handleAnalyze, open, hasFile: !!selectedFile }
  }

  const handleClear = () => {
    setSelectedFile(null)
    setPreview(null)
    setFileType(null)
    setResult(null)
  }

  return (
    <div style={{ height:'100%', display:'flex', flexDirection:'column', gap:10 }}>
      {/* Hidden input always mounted so open() works from any state */}
      <input {...getInputProps()} />

      <AnimatePresence mode="wait">

        {/* ── Drop zone (no file yet) ── */}
        {!preview && (
          <motion.div key="dropzone"
            style={{ flex:1, minHeight:200, position:'relative', borderRadius:16,
              border:'1.5px dashed rgba(255,255,255,0.08)',
              background:'rgba(10,10,26,0.6)', backdropFilter:'blur(16px)',
              cursor:'pointer', overflow:'hidden' }}
            initial={{ opacity:0, scale:.97 }} animate={{ opacity:1, scale:1 }}
            exit={{ opacity:0, scale:.97 }} transition={{ duration:0.3 }}
            {...getRootProps()}
          >

            {/* corners */}
            <Corner style={{ top:12, left:12,  borderRight:'none', borderBottom:'none' }} />
            <Corner style={{ top:12, right:12, borderLeft:'none',  borderBottom:'none' }} />
            <Corner style={{ bottom:12, left:12,  borderRight:'none', borderTop:'none' }} />
            <Corner style={{ bottom:12, right:12, borderLeft:'none',  borderTop:'none' }} />

            {/* scan line */}
            <motion.div style={{
              position:'absolute', left:0, right:0, height:1,
              background:'linear-gradient(90deg,transparent,rgba(96,165,250,0.5),transparent)',
              pointerEvents:'none',
            }}
              animate={{ top:['10%','90%','10%'] }}
              transition={{ duration:5, repeat:Infinity, ease:'easeInOut' }}
            />

            {/* center content */}
            <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column',
              alignItems:'center', justifyContent:'center', gap:12, padding:'0 24px', textAlign:'center' }}>
              <div style={{ position:'relative', display:'flex', alignItems:'center', justifyContent:'center' }}>
                <motion.div style={{ position:'absolute', width:80, height:80, borderRadius:'50%',
                  border:'1px solid rgba(59,130,246,0.12)' }}
                  animate={{ scale:[1,1.4,1], opacity:[.5,.1,.5] }}
                  transition={{ duration:3, repeat:Infinity, ease:'easeOut' }} />
                <div style={{ position:'relative', width:48, height:48, borderRadius:12,
                  background:'linear-gradient(135deg,rgba(37,99,235,0.18),rgba(124,58,237,0.18))',
                  border:'1px solid rgba(59,130,246,0.25)',
                  display:'flex', alignItems:'center', justifyContent:'center' }}>
                  <FiUpload style={{ fontSize:20, color:'#60a5fa' }} />
                </div>
              </div>
              <div>
                <p style={{ fontSize:14, fontWeight:600, color:'#e5e7eb', marginBottom:4 }}>
                  Drop image or video here
                </p>
                <p style={{ fontSize:12, color:'#6b7280' }}>or click to browse</p>
              </div>
              <div style={{ display:'flex', gap:8, flexWrap:'wrap', justifyContent:'center' }}>
                {[
                  { Icon: FiImage, label:'JPG · PNG', c:'rgba(59,130,246,0.12)', tc:'#93c5fd' },
                  { Icon: FiVideo, label:'MP4 · MOV', c:'rgba(124,58,237,0.12)', tc:'#c4b5fd' },
                ].map(({ Icon, label, c, tc }) => (
                  <div key={label} style={{ display:'flex', alignItems:'center', gap:6,
                    fontSize:11, padding:'4px 12px', borderRadius:20,
                    background:c, color:'#9ca3af', border:`1px solid ${tc}33` }}>
                    <Icon style={{ color:tc, fontSize:11 }} />
                    {label}
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* ── Preview (file loaded) ── */}
        {preview && (
          <motion.div key="preview"
            style={{ display:'flex', flexDirection:'column', gap:10 }}
            initial={{ opacity:0, scale:.97 }} animate={{ opacity:1, scale:1 }}
            exit={{ opacity:0, scale:.97 }} transition={{ duration:0.3 }}
          >
            {/* Small image preview */}
            <div style={{ position:'relative', borderRadius:12, overflow:'hidden',
              background:'rgba(10,10,26,0.7)', border:'1px solid rgba(255,255,255,0.06)',
              height:170, display:'flex', alignItems:'center', justifyContent:'center' }}>
              {fileType === 'video' ? (
                <video src={preview} controls
                  style={{ maxHeight:170, maxWidth:'100%', objectFit:'contain' }} />
              ) : (
                <img src={preview} alt="Preview"
                  style={{ maxHeight:170, maxWidth:'100%', objectFit:'contain' }} />
              )}
              {/* file badge */}
              <div style={{ position:'absolute', top:8, left:8, display:'flex', alignItems:'center',
                gap:6, background:'rgba(0,0,0,0.65)', backdropFilter:'blur(8px)',
                padding:'3px 10px', borderRadius:20 }}>
                {fileType === 'video'
                  ? <FiVideo style={{ fontSize:11, color:'#c4b5fd' }} />
                  : <FiImage style={{ fontSize:11, color:'#93c5fd' }} />
                }
                <span style={{ fontSize:11, color:'#d1d5db', maxWidth:160,
                  overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                  {selectedFile?.name}
                </span>
                <span style={{ fontSize:10, color:'#6b7280' }}>
                  {(selectedFile?.size / 1024 / 1024).toFixed(1)}MB
                </span>
              </div>
              {/* clear X */}
              <button onClick={handleClear} disabled={loading}
                style={{ position:'absolute', top:8, right:8, width:28, height:28,
                  borderRadius:'50%', background:'rgba(0,0,0,0.65)', backdropFilter:'blur(8px)',
                  border:'1px solid rgba(255,255,255,0.1)', cursor:'pointer',
                  display:'flex', alignItems:'center', justifyContent:'center',
                  opacity: loading ? 0.4 : 1 }}>
                <FiX style={{ fontSize:13, color:'#9ca3af' }} />
              </button>
            </div>

            {/* Analyze button */}
            <motion.button onClick={handleAnalyze} disabled={loading}
              style={{ width:'100%', padding:'12px 0', borderRadius:12,
                background: loading ? 'rgba(37,99,235,0.4)' : 'linear-gradient(135deg,#2563eb,#7c3aed)',
                border:'none', cursor: loading ? 'not-allowed' : 'pointer',
                color:'#fff', fontSize:13, fontWeight:700,
                letterSpacing:'0.08em', textTransform:'uppercase',
                display:'flex', alignItems:'center', justifyContent:'center', gap:8,
                boxShadow: loading ? 'none' : '0 4px 20px rgba(37,99,235,0.35)',
                position:'relative', overflow:'hidden' }}
              whileHover={!loading ? { scale:1.01 } : {}}
              whileTap={!loading ? { scale:0.99 } : {}}
            >
              {!loading && (
                <motion.div style={{
                  position:'absolute', inset:0,
                  background:'linear-gradient(90deg,transparent,rgba(255,255,255,0.08),transparent)',
                }}
                  animate={{ x:['-100%','100%'] }}
                  transition={{ duration:2, repeat:Infinity, ease:'linear' }}
                />
              )}
              <span style={{ position:'relative', zIndex:1, display:'flex', alignItems:'center', gap:8 }}>
                {loading ? (
                  <>
                    <motion.div style={{ width:14, height:14, borderRadius:'50%',
                      border:'2px solid rgba(255,255,255,0.3)', borderTopColor:'#fff' }}
                      animate={{ rotate:360 }}
                      transition={{ duration:0.8, repeat:Infinity, ease:'linear' }} />
                    Analyzing...
                  </>
                ) : (
                  <><FiZap /> Run Analysis</>
                )}
              </span>
            </motion.button>

            {/* Change image button */}
            <button onClick={open} disabled={loading}
              style={{ width:'100%', padding:'9px 0', borderRadius:12,
                background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.08)',
                cursor:'pointer', color:'#6b7280', fontSize:12, fontWeight:500,
                opacity: loading ? 0.4 : 1 }}>
              Change {fileType === 'video' ? 'Video' : 'Image'}
            </button>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  )
}
