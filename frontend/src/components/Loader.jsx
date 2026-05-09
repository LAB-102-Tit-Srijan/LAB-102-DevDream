import { Loader2 } from 'lucide-react'

const Loader = ({ fullScreen = false }) => {
  const loaderContent = (
    <div className="flex flex-col items-center justify-center gap-4">
      <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
      <p className="text-slate-400 font-medium">Loading...</p>
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center">
        {loaderContent}
      </div>
    )
  }

  return (
    <div className="w-full h-64 flex items-center justify-center">
      {loaderContent}
    </div>
  )
}

export default Loader
