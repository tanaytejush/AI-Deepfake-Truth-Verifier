import { FiActivity, FiCheckCircle, FiAlertTriangle, FiClock, FiCpu, FiTrendingUp } from 'react-icons/fi'
import { motion } from 'framer-motion'

function Statistics({ statistics }) {
  if (!statistics) {
    return (
      <div className="cyber-card text-center py-12">
        <motion.div
          className="w-16 h-16 mx-auto mb-4 rounded-full border-4 border-cyber-blue/30"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <motion.div
            className="w-full h-full rounded-full border-t-4 border-cyber-blue"
            animate={{ rotate: -360 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          />
        </motion.div>
        <p className="text-gray-400">Loading statistics...</p>
      </div>
    )
  }

  const stats = [
    {
      name: 'Total Predictions',
      value: statistics.total_predictions,
      icon: FiActivity,
      gradient: 'from-cyber-blue to-cyber-cyan',
      borderColor: 'border-cyber-blue'
    },
    {
      name: 'Real Images',
      value: statistics.real_count,
      icon: FiCheckCircle,
      gradient: 'from-cyber-green to-green-400',
      borderColor: 'border-cyber-green'
    },
    {
      name: 'Fake Images',
      value: statistics.fake_count,
      icon: FiAlertTriangle,
      gradient: 'from-red-500 to-red-600',
      borderColor: 'border-danger'
    },
    {
      name: 'Avg Confidence',
      value: `${statistics.average_confidence.toFixed(1)}%`,
      icon: FiTrendingUp,
      gradient: 'from-cyber-purple to-cyber-pink',
      borderColor: 'border-cyber-purple'
    }
  ]

  const fakePercentage = statistics.total_predictions > 0
    ? (statistics.fake_count / statistics.total_predictions * 100).toFixed(1)
    : 0

  const realPercentage = statistics.total_predictions > 0
    ? (statistics.real_count / statistics.total_predictions * 100).toFixed(1)
    : 0

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        className="text-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="text-4xl font-bold gradient-text mb-2">Statistics Dashboard</h2>
        <p className="text-gray-400 flex items-center justify-center space-x-2">
          <FiActivity className="text-cyber-blue" />
          <span>Overview of all predictions and model performance</span>
        </p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.name}
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ delay: index * 0.1, type: "spring" }}
              whileHover={{ scale: 1.05 }}
              className={`stats-card ${stat.borderColor} relative overflow-hidden`}
            >
              {/* Animated background */}
              <motion.div
                className={`absolute inset-0 bg-gradient-to-br ${stat.gradient} opacity-5`}
                animate={{
                  scale: [1, 1.1, 1],
                  opacity: [0.05, 0.1, 0.05]
                }}
                transition={{ duration: 3, repeat: Infinity }}
              />

              <div className="relative z-10 flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">{stat.name}</p>
                  <motion.p
                    className="text-4xl font-black text-gray-100"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: index * 0.1 + 0.2, type: "spring" }}
                  >
                    {stat.value}
                  </motion.p>
                </div>
                <div className={`bg-gradient-to-r ${stat.gradient} p-4 rounded-xl shadow-glow`}>
                  <Icon className="text-2xl text-white" />
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribution */}
        <motion.div
          className="cyber-card p-8"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h3 className="text-2xl font-bold gradient-text mb-6 uppercase tracking-wider">
            Prediction Distribution
          </h3>

          {statistics.total_predictions === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FiActivity className="mx-auto text-5xl mb-3 opacity-30" />
              <p>No predictions yet</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Real Images */}
              <div>
                <div className="flex justify-between text-sm mb-3">
                  <span className="text-gray-400 font-medium flex items-center space-x-2">
                    <FiCheckCircle className="text-cyber-green" />
                    <span>Real Images</span>
                  </span>
                  <span className="text-cyber-green font-bold text-lg">
                    {statistics.real_count} ({realPercentage}%)
                  </span>
                </div>
                <div className="progress-bar">
                  <motion.div
                    className="progress-fill bg-gradient-to-r from-cyber-green to-green-400"
                    initial={{ width: 0 }}
                    animate={{ width: `${realPercentage}%` }}
                    transition={{ duration: 1.5, delay: 0.6 }}
                  />
                </div>
              </div>

              {/* Fake Images */}
              <div>
                <div className="flex justify-between text-sm mb-3">
                  <span className="text-gray-400 font-medium flex items-center space-x-2">
                    <FiAlertTriangle className="text-danger" />
                    <span>Fake Images</span>
                  </span>
                  <span className="text-danger font-bold text-lg">
                    {statistics.fake_count} ({fakePercentage}%)
                  </span>
                </div>
                <div className="progress-bar">
                  <motion.div
                    className="progress-fill bg-gradient-to-r from-red-500 to-red-600"
                    initial={{ width: 0 }}
                    animate={{ width: `${fakePercentage}%` }}
                    transition={{ duration: 1.5, delay: 0.7 }}
                  />
                </div>
              </div>
            </div>
          )}
        </motion.div>

        {/* Performance */}
        <motion.div
          className="cyber-card p-8"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
        >
          <h3 className="text-2xl font-bold gradient-text mb-6 uppercase tracking-wider">
            Model Performance
          </h3>

          <div className="space-y-4">
            {/* Average Confidence */}
            <motion.div
              className="stats-card border-cyber-purple"
              whileHover={{ scale: 1.02 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Average Confidence</p>
                  <p className="text-3xl font-bold text-cyber-purple">
                    {statistics.average_confidence.toFixed(1)}%
                  </p>
                </div>
                <div className="bg-gradient-to-r from-cyber-purple to-cyber-pink p-3 rounded-xl">
                  <FiTrendingUp className="text-2xl text-white" />
                </div>
              </div>
            </motion.div>

            {/* Processing Time */}
            <motion.div
              className="stats-card border-cyber-blue"
              whileHover={{ scale: 1.02 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Avg Processing Time</p>
                  <p className="text-3xl font-bold text-cyber-blue">
                    {statistics.average_inference_time.toFixed(3)}s
                  </p>
                </div>
                <div className="bg-gradient-to-r from-cyber-blue to-cyber-cyan p-3 rounded-xl">
                  <FiClock className="text-2xl text-white" />
                </div>
              </div>
            </motion.div>

            {/* Performance Grade */}
            {statistics.total_predictions > 0 && (
              <motion.div
                className="glass-card p-4 border-l-4 border-cyber-green"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 }}
              >
                <p className="text-xs text-gray-500 mb-3 uppercase tracking-wider">Performance Grade</p>
                <div className="flex items-center space-x-3">
                  <div className="flex-1 progress-bar">
                    <motion.div
                      className="progress-fill bg-gradient-to-r from-cyber-green to-cyber-blue"
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(statistics.average_confidence, 100)}%` }}
                      transition={{ duration: 1.5, delay: 1 }}
                    />
                  </div>
                  <span className="text-sm font-bold text-gray-200 min-w-[80px] text-right">
                    {statistics.average_confidence > 90 ? 'Excellent' :
                     statistics.average_confidence > 80 ? 'Good' :
                     statistics.average_confidence > 70 ? 'Fair' : 'Poor'}
                  </span>
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Info Cards */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
      >
        <div className="glass-card p-6 border-l-4 border-cyber-blue hover:scale-105 transition-transform">
          <div className="flex items-center space-x-3 mb-2">
            <div className="bg-gradient-to-r from-cyber-blue to-cyber-cyan p-2 rounded-lg">
              <FiCpu className="text-white" />
            </div>
            <h4 className="font-bold text-gray-200 uppercase tracking-wider text-sm">Model</h4>
          </div>
          <p className="text-sm text-gray-400 ml-11">Pretrained deepfake detector</p>
        </div>

        <div className="glass-card p-6 border-l-4 border-cyber-purple hover:scale-105 transition-transform">
          <div className="flex items-center space-x-3 mb-2">
            <div className="bg-gradient-to-r from-cyber-purple to-cyber-pink p-2 rounded-lg">
              <FiTrendingUp className="text-white" />
            </div>
            <h4 className="font-bold text-gray-200 uppercase tracking-wider text-sm">Accuracy</h4>
          </div>
          <p className="text-sm text-gray-400 ml-11">85-95% on standard datasets</p>
        </div>

        <div className="glass-card p-6 border-l-4 border-cyber-green hover:scale-105 transition-transform">
          <div className="flex items-center space-x-3 mb-2">
            <div className="bg-gradient-to-r from-cyber-green to-green-400 p-2 rounded-lg">
              <FiCheckCircle className="text-white" />
            </div>
            <h4 className="font-bold text-gray-200 uppercase tracking-wider text-sm">Device</h4>
          </div>
          <p className="text-sm text-gray-400 ml-11">Optimized for M1 Mac (MPS)</p>
        </div>
      </motion.div>
    </div>
  )
}

export default Statistics
