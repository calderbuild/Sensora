'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import Image from 'next/image'
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
} from 'recharts'

// API base URL
const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '')

// Formula types
interface Ingredient {
  name: string
  concentration: number
  note_type: string
  sustainable?: boolean
}

interface Formula {
  formula_id: string
  name: string
  description: string
  ingredients: Ingredient[]
  note_pyramid: { top: number; middle: number; base: number }
  longevity_score: number
  projection_score: number
  sustainability_score: number
  ifra_compliant: boolean
  physio_corrections_applied: string[]
}

// Sample formula data (fallback)
const sampleFormula: Formula = {
  formula_id: 'sample-001',
  name: 'Kyoto Morning Rain',
  description:
    'A contemplative blend capturing the essence of dawn in a Japanese garden, where petrichor meets ancient cypress.',
  ingredients: [
    { name: 'Yuzu', concentration: 8, note_type: 'top', sustainable: true },
    { name: 'Green Tea Accord', concentration: 5, note_type: 'top', sustainable: true },
    { name: 'Hinoki Wood', concentration: 15, note_type: 'middle', sustainable: true },
    { name: 'Iris Pallida', concentration: 12, note_type: 'middle', sustainable: true },
    { name: 'Vetiver Haiti', concentration: 18, note_type: 'base', sustainable: true },
    { name: 'White Musk', concentration: 12, note_type: 'base', sustainable: true },
  ],
  note_pyramid: { top: 20, middle: 35, base: 45 },
  longevity_score: 8.5,
  projection_score: 7.2,
  sustainability_score: 9.0,
  ifra_compliant: true,
  physio_corrections_applied: ['Optimized for normal skin pH'],
}

// Scent pyramid visualization with light theme
function ScentPyramid({
  ingredients,
}: {
  ingredients: Ingredient[]
}) {
  const [activeLayer, setActiveLayer] = useState<'top' | 'middle' | 'base' | null>(null)

  const topNotes = ingredients.filter(i => i.note_type === 'top')
  const middleNotes = ingredients.filter(i => i.note_type === 'middle' || i.note_type === 'heart')
  const baseNotes = ingredients.filter(i => i.note_type === 'base')

  return (
    <div className="relative w-full max-w-md mx-auto">
      <svg viewBox="0 0 300 260" className="w-full h-auto">
        {/* Definitions */}
        <defs>
          <linearGradient id="pyramidTealGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(16, 185, 129, 0.15)" />
            <stop offset="100%" stopColor="rgba(5, 150, 105, 0.08)" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Base layer */}
        <motion.g
          className="cursor-pointer"
          onMouseEnter={() => setActiveLayer('base')}
          onMouseLeave={() => setActiveLayer(null)}
          whileHover={{ scale: 1.02 }}
        >
          <motion.path
            d="M20 180 L280 180 L240 250 L60 250 Z"
            fill={activeLayer === 'base' ? 'rgba(16, 185, 129, 0.25)' : 'rgba(16, 185, 129, 0.12)'}
            stroke="rgba(16, 185, 129, 0.4)"
            strokeWidth="1"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          />
          <text x="150" y="222" textAnchor="middle" fill="rgba(16, 185, 129, 0.9)" fontSize="12" className="font-body">
            BASE NOTES
          </text>
        </motion.g>

        {/* Middle layer */}
        <motion.g
          className="cursor-pointer"
          onMouseEnter={() => setActiveLayer('middle')}
          onMouseLeave={() => setActiveLayer(null)}
          whileHover={{ scale: 1.02 }}
        >
          <motion.path
            d="M50 100 L250 100 L280 180 L20 180 Z"
            fill={activeLayer === 'middle' ? 'rgba(16, 185, 129, 0.25)' : 'rgba(16, 185, 129, 0.08)'}
            stroke="rgba(16, 185, 129, 0.4)"
            strokeWidth="1"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          />
          <text x="150" y="145" textAnchor="middle" fill="rgba(16, 185, 129, 0.9)" fontSize="12" className="font-body">
            HEART NOTES
          </text>
        </motion.g>

        {/* Top layer */}
        <motion.g
          className="cursor-pointer"
          onMouseEnter={() => setActiveLayer('top')}
          onMouseLeave={() => setActiveLayer(null)}
          whileHover={{ scale: 1.02 }}
        >
          <motion.path
            d="M100 30 L200 30 L250 100 L50 100 Z"
            fill={activeLayer === 'top' ? 'rgba(16, 185, 129, 0.25)' : 'rgba(16, 185, 129, 0.05)'}
            stroke="rgba(16, 185, 129, 0.4)"
            strokeWidth="1"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          />
          <text x="150" y="70" textAnchor="middle" fill="rgba(16, 185, 129, 0.9)" fontSize="12" className="font-body">
            TOP NOTES
          </text>
        </motion.g>
      </svg>

      {/* Layer details popup */}
      <AnimatePresence>
        {activeLayer && (
          <motion.div
            className="absolute left-full top-1/2 -translate-y-1/2 ml-4 w-48 p-4 wellness-card"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
          >
            <h4 className="text-sensora-teal-600 text-sm font-medium mb-2 capitalize">
              {activeLayer} Notes
            </h4>
            <ul className="space-y-1">
              {(activeLayer === 'top'
                ? topNotes
                : activeLayer === 'middle'
                ? middleNotes
                : baseNotes
              ).map((note, i) => (
                <li key={i} className="flex items-center justify-between text-sm">
                  <span className="text-sensora-text">{note.name}</span>
                  <span className="text-sensora-text-muted">{note.concentration}%</span>
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Metrics radar chart with light theme
function MetricsChart({ formula }: { formula: Formula }) {
  const data = [
    { metric: 'Longevity', value: formula.longevity_score * 10 },
    { metric: 'Projection', value: formula.projection_score * 10 },
    { metric: 'Sustainability', value: formula.sustainability_score * 10 },
    { metric: 'Safety', value: formula.ifra_compliant ? 100 : 50 },
  ]

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data}>
          <PolarGrid stroke="rgba(16, 185, 129, 0.2)" />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: 'rgb(107, 114, 128)', fontSize: 11 }}
          />
          <Radar
            name="Metrics"
            dataKey="value"
            stroke="#10B981"
            fill="#10B981"
            fillOpacity={0.25}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

// Ingredient list with light theme
function IngredientList({
  ingredients,
  title,
}: {
  ingredients: Ingredient[]
  title: string
}) {
  return (
    <div className="mb-6">
      <h4 className="text-sensora-teal-600 text-sm font-medium mb-3">{title}</h4>
      <div className="space-y-2">
        {ingredients.map((ingredient, i) => (
          <motion.div
            key={i}
            className="flex items-center justify-between p-3 rounded-xl bg-sensora-gray-50 border border-sensora-teal-100"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <div className="flex items-center gap-3">
              <span className="text-sensora-text">{ingredient.name}</span>
              {ingredient.sustainable && (
                <span className="badge-teal text-xs">
                  Sustainable
                </span>
              )}
            </div>
            <span className="text-sensora-text-muted font-mono text-sm">
              {ingredient.concentration}%
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// Progress steps with light theme
function ProgressSteps({ currentStep }: { currentStep: number }) {
  const steps = ['Bio-Calibration', 'Scent Brief', 'Your Formula']

  return (
    <div className="flex items-center justify-center gap-4 mb-12">
      {steps.map((step, index) => (
        <div key={step} className="flex items-center">
          <motion.div
            className={`progress-step ${index < currentStep ? 'completed' : ''} ${
              index === currentStep ? 'active' : ''
            }`}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: index * 0.1 }}
          >
            {index < currentStep ? (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <span className="text-sm font-medium">{index + 1}</span>
            )}
          </motion.div>
          {index < steps.length - 1 && (
            <div
              className={`w-16 md:w-24 h-0.5 mx-2 transition-colors duration-500 ${
                index < currentStep ? 'bg-sensora-teal-500' : 'bg-sensora-gray-200'
              }`}
            />
          )}
        </div>
      ))}
    </div>
  )
}

// Loading animation with light theme
function LoadingAnimation() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6">
      <motion.div
        className="relative w-32 h-32"
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
      >
        {/* Orbital rings */}
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="absolute inset-0 rounded-full border border-sensora-teal-300"
            style={{
              transform: `rotateX(${60 + i * 20}deg) rotateY(${i * 30}deg)`,
            }}
            animate={{
              rotateZ: [0, 360],
            }}
            transition={{
              duration: 4 + i,
              repeat: Infinity,
              ease: 'linear',
            }}
          />
        ))}

        {/* Center glow */}
        <motion.div
          className="absolute inset-8 rounded-full bg-sensora-teal-200"
          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      </motion.div>

      <motion.div
        className="mt-8 text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <h2 className="font-display text-2xl text-sensora-text mb-2">
          Formulating Your Essence
        </h2>
        <p className="text-sensora-text-soft text-sm">
          Analyzing bio-data and synthesizing molecules...
        </p>
      </motion.div>

      {/* Progress messages */}
      <motion.div
        className="mt-6 space-y-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        {[
          'Retrieving physiological rules...',
          'Calculating molecular compatibility...',
          'Optimizing volatility curves...',
          'Applying sustainability filters...',
        ].map((msg, i) => (
          <motion.p
            key={i}
            className="text-sensora-teal-500 text-sm text-center"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: [0, 1, 0.5] }}
            transition={{ delay: 1.5 + i * 0.8, duration: 2 }}
          >
            {msg}
          </motion.p>
        ))}
      </motion.div>
    </div>
  )
}

export default function ResultPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [formula, setFormula] = useState<Formula>(sampleFormula)
  const [showQR, setShowQR] = useState(false)

  // Fetch formula from API
  const fetchFormula = useCallback(async () => {
    try {
      const calibration = localStorage.getItem('sensora_calibration')
      const neuroBrief = localStorage.getItem('sensora_neuro_brief')

      if (!calibration || !neuroBrief) {
        setFormula(sampleFormula)
        setIsLoading(false)
        return
      }

      const calData = JSON.parse(calibration)
      const neuroData = JSON.parse(neuroBrief)

      const response = await fetch(`${API_BASE}/api/formulation/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile_id: 'user-' + Date.now(),
          ph_value: calData.ph || 5.5,
          skin_type: calData.skinType || 'normal',
          temperature: calData.temperature || 36.5,
          prompt: neuroData.prompt || '',
          valence: neuroData.valence ?? 0.3,
          arousal: neuroData.arousal ?? 0.2,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to generate formula')
      }

      const data = await response.json()
      setFormula(data)
    } catch (err) {
      console.error('Error fetching formula:', err)
      setFormula(sampleFormula)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    // Add delay for loading animation then fetch
    const timer = setTimeout(() => {
      fetchFormula()
    }, 3000)

    return () => clearTimeout(timer)
  }, [fetchFormula])

  const handleExport = () => {
    const calibration = localStorage.getItem('aether_calibration')
    const neuroBrief = localStorage.getItem('aether_neuro_brief')

    const exportData = {
      formula,
      calibration: calibration ? JSON.parse(calibration) : null,
      neuroBrief: neuroBrief ? JSON.parse(neuroBrief) : null,
      exportedAt: new Date().toISOString(),
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `sensora-formula-${formula.name.toLowerCase().replace(/\s+/g, '-')}.json`
    a.click()
    URL.revokeObjectURL(url)
  }


  // Helper to get ingredients by note type
  const getIngredientsByType = (type: string) => {
    return formula.ingredients.filter(i =>
      i.note_type === type || (type === 'middle' && i.note_type === 'heart')
    )
  }

  if (isLoading) {
    return <LoadingAnimation />
  }

  return (
    <div className="min-h-screen py-8 px-6">
      {/* Header */}
      <motion.nav
        className="max-w-6xl mx-auto flex items-center justify-between mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Link href="/" className="font-display text-xl text-teal-gradient">
          SENSORA
        </Link>
        <Link href="/" className="text-sensora-text-soft hover:text-sensora-teal-600 transition-colors text-sm">
          Start Over
        </Link>
      </motion.nav>

      <div className="max-w-6xl mx-auto">
        {/* Progress */}
        <ProgressSteps currentStep={2} />

        {/* Formula header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <motion.p
            className="text-sensora-teal-600 uppercase tracking-[0.2em] text-sm mb-3 font-medium"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            Your Personalized Formula
          </motion.p>
          <motion.h1
            className="font-display text-4xl md:text-6xl text-teal-gradient mb-4"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
          >
            {formula.name}
          </motion.h1>
          <motion.p
            className="text-sensora-text-soft max-w-2xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {formula.description}
          </motion.p>
        </motion.div>

        {/* Main content grid */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Scent pyramid */}
          <motion.div
            className="wellness-card p-6 lg:col-span-1"
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
          >
            <h3 className="text-sensora-text font-display text-xl mb-6 text-center">
              Scent Architecture
            </h3>
            <ScentPyramid ingredients={formula.ingredients} />
            <p className="text-sensora-text-muted text-xs text-center mt-4">
              Hover over layers to see ingredients
            </p>
          </motion.div>

          {/* Metrics chart */}
          <motion.div
            className="wellness-card p-6 lg:col-span-1"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <h3 className="text-sensora-text font-display text-xl mb-6 text-center">
              Performance Metrics
            </h3>
            <MetricsChart formula={formula} />

            {/* Metric details */}
            <div className="grid grid-cols-2 gap-3 mt-4">
              <div className="p-2 rounded-xl bg-sensora-teal-50 border border-sensora-teal-100 text-center">
                <p className="text-sensora-teal-600 font-mono text-lg">{Math.round(formula.longevity_score * 10)}%</p>
                <p className="text-sensora-text-muted text-xs">Longevity</p>
              </div>
              <div className="p-2 rounded-xl bg-sensora-teal-50 border border-sensora-teal-100 text-center">
                <p className="text-sensora-teal-600 font-mono text-lg">{Math.round(formula.projection_score * 10)}%</p>
                <p className="text-sensora-text-muted text-xs">Projection</p>
              </div>
              <div className="p-2 rounded-xl bg-sensora-teal-50 border border-sensora-teal-100 text-center">
                <p className="text-sensora-teal-600 font-mono text-lg">{Math.round(formula.sustainability_score * 10)}%</p>
                <p className="text-sensora-text-muted text-xs">Sustainability</p>
              </div>
              <div className="p-2 rounded-xl bg-sensora-teal-50 border border-sensora-teal-100 text-center">
                <p className="text-sensora-teal-600 font-mono text-lg">{formula.ifra_compliant ? '100' : '50'}%</p>
                <p className="text-sensora-text-muted text-xs">Safety</p>
              </div>
            </div>
          </motion.div>

          {/* Ingredients list */}
          <motion.div
            className="wellness-card p-6 lg:col-span-1"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 }}
          >
            <h3 className="text-sensora-text font-display text-xl mb-6">
              Full Composition
            </h3>
            <div className="max-h-96 overflow-y-auto pr-2">
              <IngredientList ingredients={getIngredientsByType('top')} title="Top Notes" />
              <IngredientList ingredients={getIngredientsByType('middle')} title="Heart Notes" />
              <IngredientList ingredients={getIngredientsByType('base')} title="Base Notes" />
            </div>
          </motion.div>
        </div>

        {/* Physio corrections applied */}
        {formula.physio_corrections_applied.length > 0 && (
          <motion.div
            className="mt-8 wellness-card p-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            <h3 className="text-sensora-text font-display text-lg mb-4">AI Physiological Adjustments</h3>
            <div className="flex flex-wrap gap-2">
              {formula.physio_corrections_applied.map((correction, i) => (
                <span
                  key={i}
                  className="px-3 py-1 rounded-full bg-sensora-teal-50 border border-sensora-teal-200 text-sensora-teal-700 text-sm"
                >
                  {correction}
                </span>
              ))}
            </div>
          </motion.div>
        )}

        {/* Purchase section */}
        <motion.div
          className="mt-12 wellness-card p-8 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
        >
          <h3 className="font-display text-2xl text-sensora-text mb-2">Order Your Custom Fragrance</h3>
          <p className="text-sensora-text-soft mb-6">
            30ml Eau de Parfum, hand-crafted with your personalized formula
          </p>
          <div className="flex items-center justify-center gap-2 mb-6">
            <span className="text-sensora-teal-600 font-display text-4xl">$149</span>
            <span className="text-sensora-text-muted text-sm">USD</span>
          </div>

          {showQR ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center"
            >
              <div className="bg-white rounded-2xl p-4 shadow-sm border border-sensora-teal-100 inline-block mb-4">
                <Image
                  src="/paypal-qr.jpg"
                  alt="PayPal QR Code"
                  width={240}
                  height={240}
                  className="rounded-lg"
                />
              </div>
              <p className="text-sensora-text text-sm mb-1">Scan with PayPal app to pay <strong>$149.00 USD</strong></p>
              <p className="text-sensora-text-muted text-xs mb-4">After payment, email your order ID to confirm shipment</p>
              <button
                className="text-sensora-teal-600 text-sm underline underline-offset-2 hover:text-sensora-teal-700 transition-colors"
                onClick={() => setShowQR(false)}
              >
                Hide QR Code
              </button>
            </motion.div>
          ) : (
            <motion.button
              className="btn-primary text-lg px-8 py-4"
              onClick={() => setShowQR(true)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <span className="flex items-center gap-2">
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944.901C5.026.382 5.474 0 5.998 0h7.46c2.57 0 4.578.543 5.69 1.81 1.01 1.15 1.304 2.42 1.012 4.287-.023.143-.047.288-.077.437-.983 5.05-4.349 6.797-8.647 6.797H9.11l-1.272 7.24a.64.64 0 0 1-.633.544H7.076z"/>
                </svg>
                Pay with PayPal
              </span>
            </motion.button>
          )}

          <p className="text-sensora-text-muted text-xs mt-4">
            Secure payment via PayPal. Ships worldwide in 5-7 business days.
          </p>
        </motion.div>

        {/* Actions */}
        <motion.div
          className="mt-8 flex flex-col sm:flex-row gap-4 justify-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
        >
          <motion.button
            className="btn-soft"
            onClick={handleExport}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Export Formula
            </span>
          </motion.button>

          <Link href="/calibration">
            <motion.button
              className="btn-soft"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Create Another
            </motion.button>
          </Link>
        </motion.div>

        {/* IFRA compliance badge */}
        <motion.div
          className="mt-12 flex justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.1 }}
        >
          <div className="flex items-center gap-3 px-4 py-2 rounded-full bg-sensora-teal-50 border border-sensora-teal-200">
            <svg className="w-5 h-5 text-sensora-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
            <span className="text-sensora-teal-700 text-sm font-medium">IFRA 51st Amendment Compliant</span>
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="mt-16 py-8 border-t border-sensora-teal-100">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm">
          <p className="text-sensora-text-muted">
            L'Oreal Brandstorm 2026 Innovation Challenge
          </p>
          <p className="text-sensora-text-muted">
            Powered by Physio-RAG AI Technology
          </p>
        </div>
      </footer>
    </div>
  )
}
