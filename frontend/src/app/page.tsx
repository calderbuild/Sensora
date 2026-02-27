'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'

// Animated perfume bottle SVG component with light teal theme
function PerfumeBottle() {
  return (
    <motion.div
      className="relative w-64 h-80 md:w-80 md:h-96"
      animate={{ y: [0, -15, 0] }}
      transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
    >
      {/* Glow effect behind bottle */}
      <motion.div
        className="absolute inset-0 blur-3xl"
        style={{
          background: 'radial-gradient(circle, rgba(16, 185, 129, 0.25) 0%, transparent 70%)',
        }}
        animate={{ opacity: [0.5, 0.8, 0.5], scale: [1, 1.1, 1] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Bottle SVG */}
      <svg
        viewBox="0 0 200 300"
        className="w-full h-full relative z-10"
        style={{ filter: 'drop-shadow(0 0 30px rgba(16, 185, 129, 0.2))' }}
      >
        {/* Bottle cap */}
        <motion.rect
          x="70"
          y="10"
          width="60"
          height="30"
          rx="5"
          fill="url(#tealGradient)"
          initial={{ y: -5 }}
          animate={{ y: [10, 8, 10] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Bottle neck */}
        <path
          d="M80 40 L80 70 L65 90 L65 90 L135 90 L135 90 L120 70 L120 40 Z"
          fill="url(#glassGradient)"
          stroke="url(#tealGradient)"
          strokeWidth="1"
        />

        {/* Main bottle body */}
        <motion.path
          d="M50 90 Q30 120 30 180 Q30 260 100 270 Q170 260 170 180 Q170 120 150 90 Z"
          fill="url(#glassGradient)"
          stroke="url(#tealGradient)"
          strokeWidth="1.5"
          initial={{ opacity: 0.8 }}
          animate={{ opacity: [0.8, 1, 0.8] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Liquid inside */}
        <motion.path
          d="M55 130 Q40 160 40 200 Q40 250 100 258 Q160 250 160 200 Q160 160 145 130 Z"
          fill="url(#liquidGradient)"
          initial={{ y: 0 }}
          animate={{ y: [0, 3, 0] }}
          transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Liquid shimmer */}
        <motion.ellipse
          cx="85"
          cy="180"
          rx="30"
          ry="50"
          fill="url(#shimmerGradient)"
          initial={{ opacity: 0.3 }}
          animate={{ opacity: [0.3, 0.6, 0.3], cx: [85, 115, 85] }}
          transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Sensora logo on bottle */}
        <text
          x="100"
          y="195"
          textAnchor="middle"
          className="font-display"
          fill="url(#tealGradient)"
          fontSize="16"
          fontWeight="500"
        >
          SENSORA
        </text>

        {/* Decorative line */}
        <motion.line
          x1="60"
          y1="210"
          x2="140"
          y2="210"
          stroke="url(#tealGradient)"
          strokeWidth="0.5"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2, delay: 1 }}
        />

        {/* Gradients - Light Teal Theme */}
        <defs>
          <linearGradient id="tealGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#34D399" />
            <stop offset="50%" stopColor="#10B981" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>

          <linearGradient id="glassGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="rgba(255, 255, 255, 0.9)" />
            <stop offset="50%" stopColor="rgba(236, 253, 245, 0.7)" />
            <stop offset="100%" stopColor="rgba(209, 250, 229, 0.8)" />
          </linearGradient>

          <linearGradient id="liquidGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(52, 211, 153, 0.5)" />
            <stop offset="100%" stopColor="rgba(16, 185, 129, 0.7)" />
          </linearGradient>

          <radialGradient id="shimmerGradient" cx="30%" cy="30%">
            <stop offset="0%" stopColor="rgba(167, 243, 208, 0.5)" />
            <stop offset="100%" stopColor="transparent" />
          </radialGradient>
        </defs>
      </svg>

      {/* Floating mist particles */}
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 rounded-full bg-sensora-teal-400/30"
          style={{
            left: `${30 + Math.random() * 40}%`,
            top: `${20 + Math.random() * 30}%`,
          }}
          animate={{
            y: [0, -30, -60],
            opacity: [0, 0.8, 0],
            scale: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 3,
            ease: 'easeOut',
          }}
        />
      ))}
    </motion.div>
  )
}

// Feature card component with light theme
function FeatureCard({
  icon,
  title,
  description,
  delay,
}: {
  icon: React.ReactNode
  title: string
  description: string
  delay: number
}) {
  return (
    <motion.div
      className="wellness-card p-6"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ y: -5, transition: { duration: 0.2 } }}
    >
      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-sensora-teal-100 to-sensora-teal-50 flex items-center justify-center mb-4 text-sensora-teal-600">
        {icon}
      </div>
      <h3 className="font-display text-xl text-sensora-text mb-2">{title}</h3>
      <p className="text-sensora-text-soft text-sm leading-relaxed">{description}</p>
    </motion.div>
  )
}

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Decorative background blobs */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="wellness-blob w-96 h-96 bg-sensora-teal-200/30 top-0 right-0" />
        <div className="wellness-blob w-80 h-80 bg-sensora-gold-200/20 bottom-0 left-0" style={{ animationDelay: '-5s' }} />
        <div className="wellness-blob w-64 h-64 bg-sensora-rose-200/20 top-1/2 left-1/4" style={{ animationDelay: '-10s' }} />
      </div>

      {/* Navigation */}
      <motion.nav
        className="fixed top-0 left-0 right-0 z-50 px-6 py-4 bg-white/80 backdrop-blur-md border-b border-sensora-teal-100"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.div
            className="font-display text-2xl text-teal-gradient"
            whileHover={{ scale: 1.05 }}
          >
            SENSORA
          </motion.div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sensora-text-soft hover:text-sensora-teal-600 transition-colors">
              Features
            </a>
            <a href="#science" className="text-sensora-text-soft hover:text-sensora-teal-600 transition-colors">
              Science
            </a>
            <a
              href="https://github.com/calderbuild/Sensora"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sensora-text-soft hover:text-sensora-teal-600 transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="min-h-screen flex flex-col items-center justify-center px-6 pt-20">
        <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-center">
          {/* Text content */}
          <motion.div
            className="text-center md:text-left"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <motion.p
              className="text-sensora-teal-600 uppercase tracking-[0.3em] text-sm mb-4 font-medium"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              Neural Fragrance Technology
            </motion.p>

            <motion.h1
              className="font-display text-5xl md:text-7xl text-sensora-text mb-6 leading-tight"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
            >
              Your Essence,{' '}
              <span className="text-teal-gradient">Algorithmically</span>{' '}
              Perfected
            </motion.h1>

            <motion.p
              className="text-lg text-sensora-text-soft mb-8 max-w-lg mx-auto md:mx-0"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.7 }}
            >
              Sensora harnesses bio-calibration and neural interfaces to craft
              a fragrance as unique as your biochemistry. Experience perfumery
              reimagined for the individual.
            </motion.p>

            <motion.div
              className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.9 }}
            >
              <Link href="/calibration">
                <motion.button
                  className="btn-primary px-8 py-4 text-lg"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Begin Your Journey
                </motion.button>
              </Link>
              <motion.button
                className="btn-soft px-8 py-4 text-lg"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Discover the Science
              </motion.button>
            </motion.div>
          </motion.div>

          {/* Animated bottle */}
          <motion.div
            className="flex justify-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.3 }}
          >
            <PerfumeBottle />
          </motion.div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
        >
          <motion.div
            className="w-6 h-10 rounded-full border-2 border-sensora-teal-300 flex justify-center pt-2"
            animate={{ y: [0, 5, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <motion.div
              className="w-1 h-2 rounded-full bg-sensora-teal-500"
              animate={{ y: [0, 8, 0], opacity: [1, 0.3, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
          </motion.div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <p className="text-sensora-teal-600 uppercase tracking-[0.2em] text-sm mb-4 font-medium">
              The Process
            </p>
            <h2 className="font-display text-4xl md:text-5xl text-sensora-text">
              Precision <span className="text-teal-gradient">Personalization</span>
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            <FeatureCard
              icon={
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              }
              title="Bio-Calibration"
              description="Analyze your skin's unique pH, sebum levels, and temperature to understand how fragrances evolve on your body."
              delay={0.1}
            />
            <FeatureCard
              icon={
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              }
              title="Neural Interface"
              description="Our EEG integration captures your emotional responses, translating brainwave patterns into olfactory preferences."
              delay={0.2}
            />
            <FeatureCard
              icon={
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              }
              title="AI Formulation"
              description="Advanced algorithms blend molecules with precision, accounting for volatility curves and longevity optimization."
              delay={0.3}
            />
          </div>
        </div>
      </section>

      {/* Science Section */}
      <section id="science" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="wellness-card p-8 md:p-12">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              >
                <p className="text-sensora-teal-600 uppercase tracking-[0.2em] text-sm mb-4 font-medium">
                  The Science
                </p>
                <h2 className="font-display text-3xl md:text-4xl text-sensora-text mb-6">
                  Physio-Chemical{' '}
                  <span className="text-teal-gradient">Intelligence</span>
                </h2>
                <p className="text-sensora-text-soft mb-6 leading-relaxed">
                  Your skin is not a passive canvas. Its acidity affects Schiff base
                  formation in aldehydes. Its lipid content determines how long
                  molecules anchor before evaporating. Temperature accelerates
                  volatilization curves.
                </p>
                <p className="text-sensora-text-soft leading-relaxed">
                  Sensora's Physio-RAG engine retrieves from a knowledge base of
                  dermatological and chemical rules, dynamically adjusting your
                  formula for your unique biochemistry.
                </p>
              </motion.div>

              <motion.div
                className="grid grid-cols-2 gap-4"
                initial={{ opacity: 0, x: 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                {[
                  { label: 'pH Analysis', value: '4.5-7.0' },
                  { label: 'LogP Optimization', value: '>3.5' },
                  { label: 'Sustainability', value: '95%' },
                  { label: 'IFRA Compliant', value: '100%' },
                ].map((stat, i) => (
                  <div
                    key={i}
                    className="p-4 rounded-2xl bg-gradient-to-br from-sensora-teal-50 to-white border border-sensora-teal-100 text-center"
                  >
                    <p className="font-display text-2xl text-teal-gradient mb-1">
                      {stat.value}
                    </p>
                    <p className="text-sensora-text-muted text-sm">{stat.label}</p>
                  </div>
                ))}
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <motion.div
          className="max-w-3xl mx-auto text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="font-display text-4xl md:text-5xl text-sensora-text mb-6">
            Ready to Discover Your{' '}
            <span className="text-teal-gradient">Signature?</span>
          </h2>
          <p className="text-sensora-text-soft mb-8 max-w-xl mx-auto">
            The journey to your perfect fragrance begins with understanding your
            unique chemistry. Let Sensora guide you.
          </p>
          <Link href="/calibration">
            <motion.button
              className="btn-primary px-10 py-4 text-lg"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Start Bio-Calibration
            </motion.button>
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-sensora-teal-100 bg-white/50">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="font-display text-xl text-teal-gradient">SENSORA</div>
          <p className="text-sensora-text-muted text-sm">
            L'Oreal Brandstorm 2026 Innovation Challenge
          </p>
          <div className="flex gap-6">
            <a
              href="https://github.com/calderbuild/Sensora"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sensora-text-muted text-sm hover:text-sensora-teal-600 transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
