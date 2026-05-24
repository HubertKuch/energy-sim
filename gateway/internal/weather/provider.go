package weather

import (
	"context"
	"time"
)

// WeatherData represents the hourly weather information
type WeatherData struct {
	Timestamp time.Time
	GHI       float64 // Global Horizontal Irradiance (W/m2)
	DNI       float64 // Direct Normal Irradiance (W/m2)
	DHI       float64 // Diffuse Horizontal Irradiance (W/m2)
	TempAir   float64 // Ambient Temperature (C)
	WindSpeed float64 // Wind Speed (m/s)
	SnowDepth float64 // Snow Depth (cm)
}

// Provider defines the interface
type Provider interface {
	FetchHourly(ctx context.Context, lat, lon float64, start, end time.Time) ([]WeatherData, error)
}
