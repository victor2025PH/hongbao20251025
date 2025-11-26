import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Gift, Zap, Sparkles, Trophy, TrendingUp, ArrowLeft, Star } from 'lucide-react'
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
  decoration: 'stars' | 'sparkles' | 'waves' | 'circles' | 'diamonds' | 'hearts'
  probability: number
}

const prizes: Prize[] = [
  { id: 1, name: '能量', value: 100, icon: Zap, color: 'text-yellow-400', bgGradient: 'from-yellow-500/40 to-orange-500/40', decoration: 'stars', probability: 10 },
  { id: 2, name: '能量', value: 50, icon: Zap, color: 'text-yellow-400', bgGradient: 'from-yellow-500/40 to-orange-500/40', decoration: 'sparkles', probability: 20 },
  { id: 3, name: '能量', value: 30, icon: Zap, color: 'text-yellow-400', bgGradient: 'from-yellow-500/40 to-orange-500/40', decoration: 'circles', probability: 25 },
  { id: 4, name: '幸运值', value: 20, icon: Sparkles, color: 'text-purple-400', bgGradient: 'from-purple-500/40 to-pink-500/40', decoration: 'diamonds', probability: 15 },
  { id: 5, name: '幸运值', value: 10, icon: Sparkles, color: 'text-purple-400', bgGradient: 'from-purple-500/40 to-pink-500/40', decoration: 'hearts', probability: 20 },
  { id: 6, name: '经验值', value: 50, icon: TrendingUp, color: 'text-cyan-400', bgGradient: 'from-cyan-500/40 to-blue-500/40', decoration: 'waves', probability: 10 },
]

interface Particle {
  id: string
  x: number
  y: number
  vx: number
  vy: number
  size: number
  color: string
  rotation: number
  rotationSpeed: number
  scale: number
  opacity: number
  life: number
  maxLife: number
  icon: React.ElementType
}

// 粒子系统组件
function ParticleSystem({ isActive, centerX, centerY }: { isActive: boolean; centerX: number; centerY: number }) {
  const [particles, setParticles] = useState<Particle[]>([])
  const animationFrameRef = useRef<number>()

  useEffect(() => {
    if (!isActive) {
      setParticles([])
      return
    }

    // 创建初始粒子
    const newParticles: Particle[] = []
    const icons = [Zap, Sparkles, Star, Trophy, Gift, TrendingUp]
    const colors = ['#fbbf24', '#f472b6', '#8b5cf6', '#10b981', '#3b82f6', '#ec4899', '#a855f7', '#06b6d4']

    for (let i = 0; i < 50; i++) {
      const angle = (Math.PI * 2 * i) / 50 + Math.random() * 0.5
      const speed = 2 + Math.random() * 4
      const Icon = icons[Math.floor(Math.random() * icons.length)]
      const color = colors[Math.floor(Math.random() * colors.length)]

      newParticles.push({
        id: `particle-${i}-${Date.now()}`,
        x: centerX,
        y: centerY,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: 8 + Math.random() * 12,
        color,
        rotation: Math.random() * 360,
        rotationSpeed: (Math.random() - 0.5) * 10,
        scale: 0.5 + Math.random() * 0.5,
        opacity: 1,
        life: 0,
        maxLife: 60 + Math.random() * 40,
        icon: Icon,
      })
    }

    setParticles(newParticles)
  }, [isActive, centerX, centerY])

  useEffect(() => {
    if (particles.length === 0) return

    const animate = () => {
      setParticles(prev => {
        const updated = prev
          .map(p => ({
            ...p,
            x: p.x + p.vx,
            y: p.y + p.vy,
            rotation: p.rotation + p.rotationSpeed,
            life: p.life + 1,
            scale: p.scale * (1 + Math.sin(p.life * 0.1) * 0.2),
            opacity: Math.max(0, 1 - p.life / p.maxLife),
            vy: p.vy + 0.1, // 重力
          }))
          .filter(p => p.life < p.maxLife && p.opacity > 0)

        if (updated.length > 0) {
          animationFrameRef.current = requestAnimationFrame(animate)
        }
        return updated
      })
    }

    animationFrameRef.current = requestAnimationFrame(animate)
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [particles.length])

  return (
    <div className="fixed inset-0 pointer-events-none z-40">
      {particles.map(particle => {
        const Icon = particle.icon
        return (
          <motion.div
            key={particle.id}
            className="absolute"
            style={{
              left: particle.x,
              top: particle.y,
              transform: `translate(-50%, -50%) rotate(${particle.rotation}deg) scale(${particle.scale})`,
              opacity: particle.opacity,
            }}
            animate={{
              scale: [particle.scale, particle.scale * 1.5, particle.scale],
            }}
            transition={{
              duration: 0.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <div
              className="relative"
              style={{
                filter: `drop-shadow(0 0 ${particle.size / 2}px ${particle.color}) drop-shadow(0 0 ${particle.size}px ${particle.color})`,
              }}
            >
                <Icon
                size={particle.size}
                style={{
                  color: particle.color,
                  filter: `drop-shadow(0 0 4px ${particle.color})`,
                }}
              />
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}

// 扇面装饰组件
function SectorDecoration({ type, color }: { type: Prize['decoration']; color: string }) {
  const decorations = {
    stars: Array.from({ length: 3 }).map((_, i) => (
      <motion.div
        key={i}
        className="absolute"
        style={{
          left: `${20 + i * 30}%`,
          top: `${15 + i * 10}%`,
        }}
        animate={{
          rotate: [0, 360],
          scale: [1, 1.3, 1],
          opacity: [0.6, 1, 0.6],
        }}
        transition={{
          duration: 2 + i * 0.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      >
        <Star size={8} style={{ color: color.replace('text-', ''), filter: `drop-shadow(0 0 4px ${color.replace('text-', '')})` }} />
      </motion.div>
    )),
    sparkles: Array.from({ length: 4 }).map((_, i) => (
      <motion.div
        key={i}
        className="absolute"
        style={{
          left: `${15 + i * 20}%`,
          top: `${10 + i * 15}%`,
        }}
        animate={{
          scale: [0.8, 1.2, 0.8],
          opacity: [0.5, 1, 0.5],
        }}
        transition={{
          duration: 1.5 + i * 0.3,
          repeat: Infinity,
          ease: "easeInOut",
          delay: i * 0.2,
        }}
      >
        <Sparkles size={6} style={{ color: color.replace('text-', ''), filter: `drop-shadow(0 0 3px ${color.replace('text-', '')})` }} />
      </motion.div>
    )),
    waves: (
      <motion.svg
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
      >
        {[0, 1, 2].map(i => (
          <motion.path
            key={i}
            d={`M 0 ${20 + i * 20} Q 25 ${10 + i * 20} 50 ${20 + i * 20} T 100 ${20 + i * 20}`}
            fill="none"
            stroke={color.includes('yellow') ? '#fbbf24' : color.includes('purple') ? '#a855f7' : color.includes('cyan') ? '#06b6d4' : '#f472b6'}
            strokeWidth="1"
            opacity="0.4"
            animate={{
              d: [
                `M 0 ${20 + i * 20} Q 25 ${10 + i * 20} 50 ${20 + i * 20} T 100 ${20 + i * 20}`,
                `M 0 ${20 + i * 20} Q 25 ${15 + i * 20} 50 ${20 + i * 20} T 100 ${20 + i * 20}`,
                `M 0 ${20 + i * 20} Q 25 ${10 + i * 20} 50 ${20 + i * 20} T 100 ${20 + i * 20}`,
              ],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.3,
            }}
          />
        ))}
      </motion.svg>
    ),
    circles: Array.from({ length: 5 }).map((_, i) => (
      <motion.div
        key={i}
        className="absolute rounded-full border-2"
        style={{
          left: `${10 + i * 15}%`,
          top: `${10 + i * 12}%`,
          width: `${8 + i * 2}px`,
          height: `${8 + i * 2}px`,
          borderColor: color.includes('yellow') ? '#fbbf24' : color.includes('purple') ? '#a855f7' : color.includes('cyan') ? '#06b6d4' : '#f472b6',
        }}
        animate={{
          scale: [1, 1.5, 1],
          opacity: [0.3, 0.7, 0.3],
        }}
        transition={{
          duration: 2 + i * 0.4,
          repeat: Infinity,
          ease: "easeInOut",
          delay: i * 0.2,
        }}
      />
    )),
    diamonds: Array.from({ length: 3 }).map((_, i) => (
      <motion.div
        key={i}
        className="absolute"
        style={{
          left: `${20 + i * 25}%`,
          top: `${12 + i * 15}%`,
          width: '8px',
          height: '8px',
          transform: 'rotate(45deg)',
          background: color.includes('yellow') ? '#fbbf24' : color.includes('purple') ? '#a855f7' : color.includes('cyan') ? '#06b6d4' : '#f472b6',
          boxShadow: `0 0 6px ${color.replace('text-', '')}`,
        }}
        animate={{
          rotate: [45, 225, 45],
          scale: [1, 1.4, 1],
        }}
        transition={{
          duration: 2.5 + i * 0.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    )),
    hearts: Array.from({ length: 2 }).map((_, i) => (
      <motion.div
        key={i}
        className="absolute text-xs"
        style={{
          left: `${25 + i * 30}%`,
          top: `${15 + i * 20}%`,
        }}
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.6, 1, 0.6],
        }}
        transition={{
          duration: 1.8,
          repeat: Infinity,
          ease: "easeInOut",
          delay: i * 0.4,
        }}
      >
        <span style={{ color: color.includes('yellow') ? '#fbbf24' : color.includes('purple') ? '#a855f7' : color.includes('cyan') ? '#06b6d4' : '#f472b6', filter: `drop-shadow(0 0 4px ${color.includes('yellow') ? '#fbbf24' : color.includes('purple') ? '#a855f7' : color.includes('cyan') ? '#06b6d4' : '#f472b6'})` }}>♥</span>
      </motion.div>
    )),
  }

  return <div className="absolute inset-0 overflow-hidden">{decorations[type]}</div>
}

export default function LuckyWheelPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { playSound } = useSound()
  const [isSpinning, setIsSpinning] = useState(false)
  const [selectedPrize, setSelectedPrize] = useState<Prize | null>(null)
  const [rotation, setRotation] = useState(0)
  const [spinsLeft, setSpinsLeft] = useState(3)
  const wheelRef = useRef<HTMLDivElement>(null)
  const [wheelCenter, setWheelCenter] = useState({ x: 0, y: 0 })

  // 计算每个奖品的角度
  const prizeAngle = 360 / prizes.length

  // 更新转盘中心位置
  useEffect(() => {
    const updateCenter = () => {
      if (wheelRef.current) {
        const rect = wheelRef.current.getBoundingClientRect()
        setWheelCenter({
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2,
        })
      }
    }
    updateCenter()
    window.addEventListener('resize', updateCenter)
    return () => window.removeEventListener('resize', updateCenter)
  }, [])

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

      // 增强的喷花特效
      const end = Date.now() + 2000
      const colors = ['#fbbf24', '#f472b6', '#8b5cf6', '#10b981', '#3b82f6', '#ec4899', '#a855f7', '#06b6d4']
      const frame = () => {
        // 从多个角度喷发
        for (let i = 0; i < 8; i++) {
          confetti({
            particleCount: 8,
            angle: i * 45,
            spread: 60,
            origin: { x: 0.5, y: 0.5 },
            colors: colors,
            zIndex: 1000,
            gravity: 0.8,
            drift: (Math.random() - 0.5) * 0.5,
          })
        }
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
          <div className="w-10" />
        </div>

        {/* 粒子系统 */}
        <ParticleSystem isActive={isSpinning} centerX={wheelCenter.x} centerY={wheelCenter.y} />

        {/* 主要内容区域 - 不滚动 */}
        <div className="flex-1 flex flex-col items-center justify-center gap-4 p-4 min-h-0">
          {/* 转盘容器 */}
          <div ref={wheelRef} className="relative w-72 h-72 shrink-0">
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
                      className={`absolute top-0 left-1/2 w-1/2 h-1/2 origin-bottom bg-gradient-to-br ${prize.bgGradient} relative`}
                      style={{
                        clipPath: `polygon(0 0, 100% 0, 50% 100%)`,
                        border: isHighlight ? '3px solid yellow' : 'none',
                        boxShadow: isHighlight ? '0 0 30px yellow, inset 0 0 20px rgba(255,255,0,0.3)' : 'none',
                      }}
                    >
                      {/* 扇面装饰 */}
                      <SectorDecoration type={prize.decoration} color={prize.color} />
                      
                      {/* 发光效果 */}
                      <motion.div
                        className="absolute inset-0"
                        style={{
                          background: `radial-gradient(circle at 30% 30%, ${prize.color.includes('yellow') ? 'rgba(251, 191, 36, 0.4)' : prize.color.includes('purple') ? 'rgba(168, 85, 247, 0.4)' : prize.color.includes('cyan') ? 'rgba(6, 182, 212, 0.4)' : 'rgba(244, 114, 182, 0.4)'}, transparent 60%)`,
                        }}
                        animate={{
                          opacity: [0.3, 0.6, 0.3],
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          ease: "easeInOut",
                        }}
                      />
                    </div>
                    {/* 奖品图标 - 只显示图标，不显示文字 */}
                    <div
                      className="absolute top-16 left-1/2 z-10"
                      style={{
                        transform: `translateX(-50%) rotate(${prizeAngle / 2}deg)`,
                        transformOrigin: 'center',
                      }}
                    >
                      <motion.div
                        animate={isSpinning ? {
                          rotate: [0, 360],
                          scale: [1, 1.2, 1],
                        } : {
                          scale: 1,
                        }}
                        transition={{
                          duration: 1,
                          repeat: isSpinning ? Infinity : 0,
                          ease: "easeInOut",
                        }}
                        className="relative"
                      >
                        <div
                          className="absolute inset-0 blur-md"
                          style={{
                            background: prize.color.includes('yellow') ? '#fbbf24' : prize.color.includes('purple') ? '#a855f7' : prize.color.includes('cyan') ? '#06b6d4' : '#f472b6',
                            opacity: 0.5,
                          }}
                        />
                        <Icon
                          size={32}
                          className={prize.color}
                          style={{
                            filter: `drop-shadow(0 0 8px currentColor) drop-shadow(0 0 16px currentColor)`,
                            position: 'relative',
                            zIndex: 1,
                          }}
                        />
                      </motion.div>
                    </div>
                  </div>
                )
              })}

              {/* 中心圆 */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 bg-gradient-to-br from-purple-600 via-pink-600 to-purple-600 rounded-full border-4 border-white/30 flex items-center justify-center shadow-2xl z-10">
                <motion.div
                  animate={isSpinning ? {
                    rotate: [0, 360],
                    scale: [1, 1.1, 1],
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
              <motion.div
                className="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-8 bg-yellow-400 rounded-full border-4 border-white/50 shadow-lg"
                animate={{
                  scale: [1, 1.1, 1],
                  boxShadow: [
                    '0 0 10px rgba(251, 191, 36, 0.5)',
                    '0 0 20px rgba(251, 191, 36, 0.8)',
                    '0 0 10px rgba(251, 191, 36, 0.5)',
                  ],
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
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
