package simulation

import (
	"context"
	"math"
	"time"

	pb "github.com/hubertkuch/solar/gateway/pb"
)

// GetWeather fetches or generates weather data for a given location and timeframe.
func (s *simulationService) GetWeather(ctx context.Context, params SolveParams) ([]*pb.WeatherData, error) {
	var weatherData []*pb.WeatherData

	if s.weatherProvider != nil && params.Location != nil {
		startTime := params.When
		endTime := startTime.Add(params.Duration)
		realWeather, err := s.weatherProvider.FetchHourly(ctx, params.Location.Latitude, params.Location.Longitude, startTime, endTime)
		if err == nil && len(realWeather) > 0 {
			for _, w := range realWeather {
				weatherData = append(weatherData, &pb.WeatherData{
					Timestamp:   w.Timestamp.Format("2006-01-02 15:04:05"),
					Ghi:         w.GHI,
					Dni:         w.DNI,
					Dhi:         w.DHI,
					TempAir:     w.TempAir,
					WindSpeed:   w.WindSpeed,
					SnowDepthCm: w.SnowDepth,
				})
			}
			return weatherData, nil
		}
	}

	startTime := params.When
	hours := int(params.Duration.Hours())
	if hours == 0 {
		hours = 1
	}

	for h := 0; h < hours; h++ {
		ts := startTime.Add(time.Duration(h) * time.Hour)
		ghi := 0.0
		hourFloat := float64(ts.Hour())
		if hourFloat >= 6 && hourFloat <= 18 {
			ghi = 1000 * math.Exp(-math.Pow(hourFloat-12, 2)/16)
		}

		weatherData = append(weatherData, &pb.WeatherData{
			Timestamp:   ts.Format("2006-01-02 15:04:05"),
			Ghi:         ghi,
			Dni:         ghi * 0.8,
			Dhi:         ghi * 0.2,
			TempAir:     params.Temperature,
			WindSpeed:   2,
			SnowDepthCm: params.SnowDepthCm,
		})
	}
	return weatherData, nil
}
