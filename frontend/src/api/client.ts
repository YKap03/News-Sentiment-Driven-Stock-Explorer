/**
 * API client for backend communication.
 */
import type {
  Ticker,
  SummaryResponse,
  ModelMetrics
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function fetchAPI<T>(endpoint: string): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `API error: ${response.status} ${response.statusText}`;
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorMessage;
      } catch {
        // If not JSON, use the text
        if (errorText) {
          errorMessage = errorText;
        }
      }
      throw new Error(errorMessage);
    }
    return response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to fetch data from API');
  }
}

export async function getTickers(): Promise<Ticker[]> {
  return fetchAPI<Ticker[]>('/api/tickers');
}

export async function getSummary(
  ticker: string,
  startDate: string,
  endDate: string
): Promise<SummaryResponse> {
  const params = new URLSearchParams({
    ticker,
    start_date: startDate,
    end_date: endDate
  });
  return fetchAPI<SummaryResponse>(`/api/summary?${params}`);
}

export async function getModelMetrics(): Promise<ModelMetrics> {
  return fetchAPI<ModelMetrics>('/api/model-metrics');
}

