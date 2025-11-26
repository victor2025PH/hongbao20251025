import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Gift, Zap, Sparkles, Trophy, TrendingUp, ArrowLeft } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'
import { useSound } from '../hooks/useSound'
import { useNavigate } from 'react-router-dom'
import PageTransition from '../components/PageTransition'
import confetti from 'canvas-confetti'

interface Prize {
  id: number
  name: string
  value: number
  icon: React.ElementType
  color: string
  bgGradient: string
  probability: number // 概率权重
}

const prizes: Prize[] = [
  { id: 1, name: '能量', value: 100, icon: Zap, color: 'text-yellow-400', bgGradient: 'from-yellow-500/30 to-orange-500/30', probability: 10 },
  { id: 2, name: '能量', value: 50, icon: Zap, color: 'text-yellow-400', bgGradient: 'from-yellow-500/30 to-orange-500/30', probability: 20 },
  { id: 3, name: '能量', value: 30, icon: Zap, color: 'text-yellow-400', bgGradient: 'from-yellow-500/30 to-orange-500/30', probability: 25 },
  { id: 4, name: '幸运值', value: 20, icon: Sparkles, color: 'text-purple-400', bgGradient: 'from-purple-500/30 to-pink-500/30', probability: 15 },
  { id: 5, name: '幸运值', value: 10, icon: Sparkles, color: 'text-purple-400', bgGradient: 'from-purple-500/30 to-pink-500/30', probability: 20 },
  { id: 6, name: '经验值', value: 50, icon: TrendingUp, color: 'text-cyan-400', bgGradient: 'from-cyan-500/30 to-blue-500/30', probability: 10 },
]

export default function LuckyWheelPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { playSound } = useSound()
  const [isSpinning, setIsSpinning] = useState(false)
  const [selectedPrize, setSelectedPrize] = useState<Prize | null>(null)
  const [rotation, setRotation] = useState(0)
  const [spinsLeft, setSpinsLeft] = useState(3) // 每日免费次数

  // 计算每个奖品的角度
  const prizeAngle = 360 / prizes.length

  // 抽奖逻辑
  const spinWheel = () => {
    if (isSpinning || spinsLeft <= 0) return

    playSound('grab')
    setIsSpinning(true)

    // 根据概率选择奖品
    const totalWeight = prizes.reduce((sum, p) => sum + p.probability, 0)
    let random = Math.random() * totalWeight
    let selected: Prize | null = null

    for (const prize of prizes) {
      random -= prize.probability
      if (random <= 0) {
        selected = prize
        break
      }
    }

    if (!selected) selected = prizes[prizes.length - 1]

    // 计算旋转角度（多转几圈 + 目标角度）
    const targetIndex = prizes.findIndex(p => p.id === selected!.id)
    const targetAngle = targetIndex * prizeAngle
    const spins = 5 * 360 // 转5圈
    const finalRotation = rotation + spins + (360 - targetAngle)

    setRotation(finalRotation)

    // 动画结束后显示结果
    setTimeout(() => {
      setSelectedPrize(selected)
      setIsSpinning(false)
      setSpinsLeft(prev => prev - 1)
      playSound('success')

      // 喷花特效
      const end = Date.now() + 1000
      const colors = ['#fbbf24', '#f472b6', '#8b5cf6', '#10b981']
      const frame = () => {
        confetti({
          particleCount: 5,
          angle: 60,
          spread: 55,
          origin: { x: 0 },
          colors: colors,
          zIndex: 1000,
        })
        confetti({
          particleCount: 5,
          angle: 120,
          spread: 55,
          origin: { x: 1 },
          colors: colors,
          zIndex: 1000,
        })
        if (Date.now() < end) {
          requestAnimationFrame(frame)
        }
      }
      frame()
    }, 3000)
  }

  return (
    <PageTransition>
      <div className="h-full flex flex-col overflow-hidden">
        {/* 顶部标题栏 */}
        <div className="flex items-center justify-between px-4 py-3 shrink-0 border-b border-white/5">
          <button
            onClick={() => navigate(-1)}
            className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center hover:bg-white/10 transition-colors"
          >
            <ArrowLeft size={20} className="text-white" />
          </button>
          <h1 className="text-lg font-bold text-white flex items-center gap-2">
            <Trophy size={20} className="text-yellow-400" />
            幸运转盘
          </h1>
          <div className="w-10" /> {/* 占位 */}
        </div>

        {/* 主要内容区域 - 不滚动 */}
        <div className="flex-1 flex flex-col items-center justify-center gap-4 p-4 min-h-0">
          {/* 转盘容器 */}
          <div className="relative w-72 h-72 shrink-0">
            {/* 转盘背景 */}
            <motion.div
              className="w-full h-full rounded-full border-4 border-purple-500/40 relative overflow-hidden bg-gradient-to-br from-purple-900/30 via-pink-900/30 to-purple-900/30 shadow-2xl"
              animate={{ rotate: rotation }}
              transition={{ 
                duration: isSpinning ? 3 : 0,
                ease: "easeOut"
              }}
            >
              {/* 奖品扇形 */}
              {prizes.map((prize, index) => {
                const Icon = prize.icon
                const angle = index * prizeAngle
                const isHighlight = selectedPrize?.id === prize.id

                return (
                  <div
                    key={prize.id}
                    className="absolute inset-0"
                    style={{
                      transform: `rotate(${angle}deg)`,
                      transformOrigin: 'center',
                    }}
                  >
                    <div
                      className={`absolute top-0 left-1/2 w-1/2 h-1/2 origin-bottom bg-gradient-to-br ${prize.bgGradient}`}
                      style={{
                        clipPath: `polygon(0 0, 100% 0, 50% 100%)`,
                        border: isHighlight ? '3px solid yellow' : 'none',
                        boxShadow: isHighlight ? '0 0 20px yellow' : 'none',
                      }}
                    />
                    {/* 奖品内容 */}
                    <div
                      className="absolute top-12 left-1/2"
                      style={{
                        transform: `translateX(-50%) rotate(${prizeAngle / 2}deg)`,
                        transformOrigin: 'center',
                      }}
                    >
                      <div className="flex flex-col items-center gap-1">
                        <Icon size={24} className={prize.color} />
                        <div className={`text-xs font-black ${prize.color} whitespace-nowrap`}>
                          {prize.value}
                        </div>
                        <div className={`text-[9px] font-bold ${prize.color} opacity-80`}>
                          {prize.name}
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}

              {/* 中心圆 */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 bg-gradient-to-br from-purple-600 via-pink-600 to-purple-600 rounded-full border-4 border-white/30 flex items-center justify-center shadow-2xl z-10">
                <motion.div
                  animate={isSpinning ? {
                    rotate: [0, 360],
                  } : {}}
                  transition={{ duration: 0.5, repeat: Infinity, ease: "linear" }}
                >
                  <Gift size={28} className="text-white drop-shadow-lg" />
                </motion.div>
              </div>
            </motion.div>

            {/* 指针 */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1 z-30">
              <div className="w-0 h-0 border-l-[18px] border-r-[18px] border-t-[35px] border-l-transparent border-r-transparent border-t-yellow-400 drop-shadow-2xl" />
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-8 bg-yellow-400 rounded-full border-4 border-white/50 shadow-lg" />
            </div>
          </div>

          {/* 剩余次数和抽奖按钮 */}
          <div className="w-full max-w-sm space-y-3 shrink-0">
            {/* 剩余次数 */}
            <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles size={18} className="text-purple-400" />
                <span className="text-sm text-gray-300">今日剩余次数</span>
              </div>
              <span className="text-2xl font-bold text-purple-400">{spinsLeft}</span>
            </div>

            {/* 抽奖按钮 */}
            <motion.button
              onClick={spinWheel}
              disabled={isSpinning || spinsLeft <= 0}
              className={`w-full py-4 rounded-xl font-bold text-base shadow-lg transition-all flex items-center justify-center gap-2 ${
                isSpinning || spinsLeft <= 0
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white active:scale-[0.98]'
              }`}
              whileHover={!isSpinning && spinsLeft > 0 ? { scale: 1.02 } : {}}
              whileTap={!isSpinning && spinsLeft > 0 ? { scale: 0.98 } : {}}
            >
              {isSpinning ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                  />
                  转盘中...
                </>
              ) : spinsLeft <= 0 ? (
                '今日次数已用完'
              ) : (
                <>
                  <Trophy size={20} />
                  开始抽奖
                </>
              )}
            </motion.button>
          </div>
        </div>

        {/* 结果弹窗 */}
        <AnimatePresence>
          {selectedPrize && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                onClick={() => setSelectedPrize(null)}
              />
              <motion.div
                initial={{ scale: 0.5, opacity: 0, y: 50 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.5, opacity: 0, y: 50 }}
                className="relative bg-[#1C1C1E] border border-purple-500/30 rounded-3xl p-8 text-center shadow-2xl max-w-sm w-full"
              >
                <motion.div
                  animate={{ rotate: [0, 360] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className={`w-20 h-20 mx-auto mb-4 bg-gradient-to-br ${selectedPrize.bgGradient} rounded-full flex items-center justify-center border-4 border-white/20`}
                >
                  <selectedPrize.icon size={40} className={selectedPrize.color} />
                </motion.div>
                <h2 className="text-2xl font-bold text-white mb-2">恭喜获得！</h2>
                <p className={`text-4xl font-black ${selectedPrize.color} mb-1`}>
                  +{selectedPrize.value}
                </p>
                <p className={`text-lg font-bold ${selectedPrize.color} mb-6`}>
                  {selectedPrize.name}
                </p>
                <motion.button
                  onClick={() => setSelectedPrize(null)}
                  className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-bold"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  太棒了！
                </motion.button>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </PageTransition>
  )
}
