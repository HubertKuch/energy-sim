package weather

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestOpenMeteoProvider_FetchHourly(t *testing.T) {
	mockResponse := `{
		"hourly": {
			"time": ["2024-01-01T00:00", "2024-01-01T01:00"],
			"temperature_2m": [10.5, 11.0],
			"wind_speed_10m": [3.6, 7.2],
			"shortwave_radiation": [0.0, 100.0],
			"direct_radiation": [0.0, 80.0],
			"diffuse_radiation": [0.0, 20.0],
			"snow_depth": [0.0, 0.05]
		}
	}`

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(mockResponse))
	}))
	defer server.Close()

	provider := NewOpenMeteoProvider()
	provider.baseURL = server.URL

	start := time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC)
	end := time.Date(2024, 1, 1, 1, 0, 0, 0, time.UTC)

	data, err := provider.FetchHourly(context.Background(), 52.2, 21.0, start, end)
	if err != nil {
		t.Fatalf("FetchHourly failed: %v", err)
	}

	if len(data) != 2 {
		t.Fatalf("expected 2 items, got %d", len(data))
	}

	if data[1].TempAir != 11.0 {
		t.Errorf("expected temp 11.0, got %f", data[1].TempAir)
	}

	if data[1].WindSpeed != 2.0 { // 7.2 km/h = 2 m/s
		t.Errorf("expected wind 2.0, got %f", data[1].WindSpeed)
	}

	if data[1].SnowDepth != 5.0 { // 0.05 m = 5 cm
		t.Errorf("expected snow 5.0, got %f", data[1].SnowDepth)
	}
}
