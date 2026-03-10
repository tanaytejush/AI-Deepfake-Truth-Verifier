import { useState, useEffect } from 'react'
import { FiClock, FiCheckCircle, FiAlertTriangle, FiTrash2, FiDatabase } from 'react-icons/fi'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'

function History() {
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(true)
  const [offline, setOffline] = useState(false)

  const fetchHistory = async () => {
    setLoading(true)
    setOffline(false)
    try {
      const response = await fetch('/api/v1/predictions/recent?limit=20')
      if (!response.ok) throw new Error('Failed to fetch')
      const data = await response.json()
      setPredictions(data.predictions || [])
    } catch (error) {
      setOffline(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [])

  const handleClearHistory = async () => {
    if (!confirm('Are you sure you want to clear all prediction history?')) {
      return
    }

    try {
      await fetch('/api/v1/predictions/clear', {
        method: 'DELETE'
      })
      setPredictions([])
      toast.success('History cleared')
    } catch (error) {
      console.error('Failed to clear history:', error)
      toast.error('Failed to clear history')
    }
  }

  if (loading) {
    return (
      <div style={{ display:'flex', alignItems:'center', justifyContent:'center', minHeight:300 }}>
        <div style={{ textAlign:'center' }}>
          <motion.div
            style={{ width:48, height:48, margin:'0 auto 16px', borderRadius:'50%',
              border:'2px solid rgba(59,130,246,0.2)', borderTopColor:'#60a5fa' }}
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
          <p style={{ color:'#9ca3af', fontSize:14 }}>Loading history...</p>
        </div>
      </div>
    )
  }

  if (offline) {
    return (
      <div style={{ display:'flex', alignItems:'center', justifyContent:'center', minHeight:300 }}>
        <div style={{ textAlign:'center', maxWidth:340 }}>
          <div style={{
            width:56, height:56, margin:'0 auto 20px', borderRadius:14,
            display:'flex', alignItems:'center', justifyContent:'center',
            background:'rgba(239,68,68,0.1)', border:'1px solid rgba(239,68,68,0.2)',
          }}>
            <FiDatabase style={{ fontSize:24, color:'#f87171' }} />
          </div>
          <p style={{ fontSize:16, fontWeight:600, color:'#f3f4f6', marginBottom:8 }}>
            Backend Offline
          </p>
          <p style={{ fontSize:13, color:'#6b7280', marginBottom:20, lineHeight:1.6 }}>
            Start the backend server to view history:
            <br />
            <code style={{ fontSize:11, color:'#93c5fd', background:'rgba(59,130,246,0.1)',
              padding:'4px 8px', borderRadius:6, display:'inline-block', marginTop:8 }}>
              uvicorn app.main:app --port 8001
            </code>
          </p>
          <button onClick={fetchHistory}
            style={{
              padding:'8px 24px', borderRadius:10, border:'1px solid rgba(59,130,246,0.3)',
              background:'rgba(59,130,246,0.1)', color:'#93c5fd',
              fontSize:13, fontWeight:600, cursor:'pointer',
            }}>
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        className="text-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="text-4xl font-bold gradient-text mb-2">Prediction History</h2>
        <p className="text-gray-400 flex items-center justify-center space-x-2 mb-4">
          <FiDatabase className="text-cyber-blue" />
          <span>View all recent predictions ({predictions.length} total)</span>
        </p>

        {predictions.length > 0 && (
          <motion.button
            onClick={handleClearHistory}
            className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl font-bold shadow-glow-lg hover:shadow-neon transition-all mx-auto"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FiTrash2 />
            <span>Clear History</span>
          </motion.button>
        )}
      </motion.div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {predictions.length === 0 ? (
          <motion.div
            key="empty"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="cyber-card text-center py-16"
          >
            <motion.div
              animate={{
                scale: [1, 1.1, 1],
                rotate: [0, 5, -5, 0]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="inline-block mb-6"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyber-blue to-cyber-purple rounded-full blur-2xl opacity-30"></div>
                <div className="relative bg-gradient-to-br from-cyber-blue/20 to-cyber-purple/20 p-8 rounded-full border border-cyber-blue/30">
                  <FiClock className="text-6xl text-cyber-blue" />
                </div>
              </div>
            </motion.div>
            <p className="text-xl text-gray-300 font-bold mb-2">No predictions yet</p>
            <p className="text-sm text-gray-500">Upload an image to get started</p>
          </motion.div>
        ) : (
          <motion.div
            key="history"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            {predictions.map((pred, index) => {
              const isFake = pred.prediction === 'FAKE'
              const Icon = isFake ? FiAlertTriangle : FiCheckCircle
              const gradient = isFake ? 'from-red-500 to-red-600' : 'from-cyber-green to-green-400'
              const borderColor = isFake ? 'border-danger' : 'border-cyber-green'

              return (
                <motion.div
                  key={pred.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ scale: 1.01, x: 5 }}
                  className={`cyber-card p-6 border-l-4 ${borderColor} relative overflow-hidden`}
                >
                  {/* Background gradient */}
                  <div className={`absolute inset-0 bg-gradient-to-r ${gradient} opacity-5`}></div>

                  <div className="relative z-10 flex items-center justify-between">
                    {/* Left section */}
                    <div className="flex items-center space-x-4 flex-1">
                      {/* Icon */}
                      <motion.div
                        className={`bg-gradient-to-r ${gradient} p-4 rounded-xl shadow-glow`}
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.5 }}
                      >
                        <Icon className="text-2xl text-white" />
                      </motion.div>

                      {/* File info */}
                      <div className="flex-1">
                        <p className="font-bold text-gray-200 mb-1 truncate max-w-md">
                          {pred.filename}
                        </p>
                        <p className="text-xs text-gray-500 flex items-center space-x-2">
                          <FiClock className="text-cyber-blue" />
                          <span>{new Date(pred.created_at).toLocaleString()}</span>
                        </p>
                      </div>
                    </div>

                    {/* Right section - Stats */}
                    <div className="flex items-center space-x-6">
                      {/* Prediction */}
                      <div className="text-center">
                        <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Result</p>
                        <p className={`text-2xl font-black ${isFake ? 'text-danger' : 'text-success'}`}>
                          {pred.prediction}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {pred.confidence.toFixed(1)}%
                        </p>
                      </div>

                      {/* Real probability */}
                      <div className="text-center min-w-[70px]">
                        <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Real</p>
                        <div className="glass-card px-3 py-2 border-l-2 border-cyber-green">
                          <p className="font-bold text-cyber-green">
                            {pred.real_probability.toFixed(1)}%
                          </p>
                        </div>
                      </div>

                      {/* Fake probability */}
                      <div className="text-center min-w-[70px]">
                        <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Fake</p>
                        <div className="glass-card px-3 py-2 border-l-2 border-danger">
                          <p className="font-bold text-danger">
                            {pred.fake_probability.toFixed(1)}%
                          </p>
                        </div>
                      </div>

                      {/* Processing time */}
                      <div className="text-center min-w-[80px]">
                        <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Time</p>
                        <div className="glass-card px-3 py-2 border-l-2 border-cyber-blue">
                          <p className="font-bold text-cyber-blue">
                            {pred.inference_time.toFixed(3)}s
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default History
