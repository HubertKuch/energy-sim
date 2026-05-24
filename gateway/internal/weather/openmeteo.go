package weather

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// OpenMeteoProvider implements the Provider interface using the Open-Meteo API.
type OpenMeteoProvider struct {
	client  *http.Client
	baseURL string
}

func NewOpenMeteoProvider() *OpenMeteoProvider {
	return &OpenMeteoProvider{
		client:  &http.Client{Timeout: 10 * time.Second},
		baseURL: "https://archive-api.open-meteo.com/v1/archive",
	}
}

type openMeteoResponse struct {
	Hourly struct {
		Time               []string  `json:"time"`
		Temperature2m      []float64 `json:"temperature_2m"`
		WindSpeed10m       []float64 `json:"wind_speed_10m"`
		ShortwaveRadiation []float64 `json:"shortwave_radiation"` // GHI
		DirectRadiation    []float64 `json:"direct_radiation"`    // DNI on horizontal
		DiffuseRadiation   []float64 `json:"diffuse_radiation"`   // DHI
		SnowDepth          []float64 `json:"snow_depth"`          // in meters, we need cm
	} `json:"hourly"`
}

func (p *OpenMeteoProvider) FetchHourly(ctx context.Context, lat, lon float64, start, end time.Time) ([]WeatherData, error) {
	url := fmt.Sprintf(
		"%s?latitude=%f&longitude=%f&start_date=%s&end_date=%s&hourly=temperature_2m,wind_speed_10m,shortwave_radiation,direct_radiation,diffuse_radiation,snow_depth&timezone=UTC",
		p.baseURL, lat, lon, start.Format("2006-01-02"), end.Format("2006-01-02"),
	)

	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, err
	}

	resp, err := p.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("open-meteo api error: status %d", resp.StatusCode)
	}

	var omResp openMeteoResponse
	if err := json.NewDecoder(resp.Body).Decode(&omResp); err != nil {
		return nil, err
	}

	results := make([]WeatherData, 0, len(omResp.Hourly.Time))
	for i, tStr := range omResp.Hourly.Time {
		t, err := time.Parse("2006-01-02T15:04", tStr)
		if err != nil {
			continue
		}

		if t.Before(start) || t.After(end) {
			continue
		}

		results = append(results, WeatherData{
			Timestamp: t,
			TempAir:   omResp.Hourly.Temperature2m[i],
			WindSpeed: omResp.Hourly.WindSpeed10m[i] / 3.6, // km/h to m/s
			GHI:       omResp.Hourly.ShortwaveRadiation[i],
			DNI:       omResp.Hourly.DirectRadiation[i],
			DHI:       omResp.Hourly.DiffuseRadiation[i],
			SnowDepth: omResp.Hourly.SnowDepth[i] * 100, // meters to cm
		})
	}

	return results, nil
}
