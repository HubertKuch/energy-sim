package simulation

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	pb "github.com/hubertkuch/solar/gateway/pb"
)

type mockSimulationService struct {
	lastParams SolveParams
}

func (m *mockSimulationService) RunSimulation(ctx context.Context, req *SimulationRequest) (*SimulationResponse, error) {
	return &SimulationResponse{
		AcOutput:   []float64{1.2, 3.4},
		Timestamps: []string{"T1", "T2"},
	}, nil
}

func (m *mockSimulationService) Solve(ctx context.Context, params SolveParams, weatherData []*pb.WeatherData) (*SimulationResponse, error) {
	m.lastParams = params
	return &SimulationResponse{
		AcOutput:   []float64{5.6},
		Timestamps: []string{"T3"},
	}, nil
}

func (m *mockSimulationService) GetWeather(ctx context.Context, params SolveParams) ([]*pb.WeatherData, error) {
	return []*pb.WeatherData{{Timestamp: "T3"}}, nil
}

func TestHandleSimulation(t *testing.T) {
	service := &mockSimulationService{}
	handler := NewSimulationHandler(service)

	reqBody, _ := json.Marshal(SimulationRequest{
		Date: "2026-06-21",
	})
	req, _ := http.NewRequest("POST", "/api/simulation", bytes.NewBuffer(reqBody))
	rr := httptest.NewRecorder()

	handler.HandleSimulation(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}

	var res SimulationResponse
	json.NewDecoder(rr.Body).Decode(&res)
	if len(res.AcOutput) != 2 {
		t.Errorf("Expected 2 outputs, got %d", len(res.AcOutput))
	}
}

func TestHandleSolve(t *testing.T) {
	service := &mockSimulationService{}
	handler := NewSimulationHandler(service)

	reqBody, _ := json.Marshal(SolveRequest{
		Duration: "10h",
		When:     "2026-06-21T12:00:00Z",
	})
	req, _ := http.NewRequest("POST", "/api/solve", bytes.NewBuffer(reqBody))
	rr := httptest.NewRecorder()

	handler.HandleSolve(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}

	if service.lastParams.Duration.Hours() != 10 {
		t.Errorf("Expected 10h duration, got %v", service.lastParams.Duration)
	}
}
