// frontend/src/features/generate/useGenerateStream.ts

import { useState } from "react"

export interface GeneratePostRequest {
  topic: string
  post_type?: string
  mode?: string
  tone?: string
  audience?: string
  context?: string
  content_type?: string
  github_url?: string
  text_input?: string
  user_key_message?: string
  tags_people?: string[]
  tags_organizations?: string[]
  include_hashtags?: boolean
  include_caption?: boolean
  additional_context?: string
  max_length?: number
}

export interface GeneratePostResponse {
  post: string
  hashtags: string
  quality_score: number
  post_id: string
  mode_used: string
  node_trace?: string[]
  has_history?: boolean
}

interface StreamState {
  isStreaming: boolean
  currentStep: string
  stepMessage: string
  result: GeneratePostResponse | null
  error: string | null
}

export function useGenerateStream(token: string | undefined) {
  const [state, setState] = useState<StreamState>({
    isStreaming:  false,
    currentStep:  "",
    stepMessage:  "",
    result:       null,
    error:        null,
  })

  const generate = async (payload: GeneratePostRequest) => {
    if (!token) {
      setState(s => ({ ...s, error: "Authentication token missing" }))
      return
    }

    setState(s => ({ ...s, isStreaming: true, result: null, error: null }))

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/posts/generate/stream`,
        {
          method:  "POST",
          headers: {
            "Content-Type":  "application/json",
            "Authorization": `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        }
      )

      if (!res.ok) {
        const errorData = await res.json()
        const detail = errorData.detail
        let errorMessage = "Generation failed"
        
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail)) {
          errorMessage = detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ')
        } else if (typeof detail === 'object' && detail !== null) {
          errorMessage = detail.msg || JSON.stringify(detail)
        }
        
        throw new Error(errorMessage)
      }

      const reader = res.body?.getReader()
      if (!reader) {
        throw new Error("Failed to initialize stream reader")
      }

      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value)
        const lines = text.split("\n").filter(l => l.startsWith("data: "))

        for (const line of lines) {
          const raw = line.replace("data: ", "").trim()
          if (raw === "[DONE]") {
            setState(s => ({ ...s, isStreaming: false }))
            return
          }

          try {
            const event = JSON.parse(raw)

            if (event.type === "progress") {
              setState(s => ({
                ...s,
                currentStep: event.step,
                stepMessage: event.message,
              }))
            }

            if (event.type === "result") {
              setState(s => ({ ...s, result: event.data }))
            }

            if (event.type === "error") {
              setState(s => ({ ...s, error: event.message, isStreaming: false }))
            }
          } catch (e) {
            console.error("Error parsing stream event:", e)
          }
        }
      }
    } catch (err: any) {
      console.error("Generate error:", err)
      setState(s => ({ ...s, error: err.message, isStreaming: false }))
    }
  }

  return { ...state, generate }
}
