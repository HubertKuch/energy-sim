package main

import (
	"context"
	"testing"
	"time"

	pb "github.com/hubertkuch/solar/gateway/pb"
	"google.golang.org/grpc"
)

type mockSolarSolverClient struct {
	pb.SolarSolverClient
	lastReq *pb.SolarRequest
}

func (m *mockSolarSolverClient) Solve(ctx context.Context, in *pb.SolarRequest, opts ...grpc.CallOption) (*pb.SolarResponse, error) {
	m.lastReq = in
	return &pb.SolarResponse{
		AcOutput:   []float64{100.0, 200.0},
		Timestamps: []string{"2026-06-21T12:00:00Z", "2026-06-21T13:00:00Z"},
	}, nil
}

func TestSimulationService_RunSimulation(t *testing.T) {
	mockClient := &mockSolarSolverClient{}
	service := NewSimulationService(mockClient)

	req := &SimulationRequest{
		Date: "2026-06-21",
		Location: &pb.Location{
			Latitude: 52.2, Longitude: 21.0, Tz: "UTC",
		},
		SystemConfig: &SystemConfig{
			Arrays: []SolarArray{
				{
					SurfaceTilt: 30, SurfaceAzimuth: 180, ModulesPerString: 10, Strings: 2,
					Panel: &SolarPanel{Pdc0: 300},
				},
			},
			Inverter: &SolarInverter{Pdc0: 5000},
		},
	}

	res, err := service.RunSimulation(context.Background(), req)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}

	if len(res.AcOutput) != 2 {
		t.Errorf("Expected 2 outputs, got %d", len(res.AcOutput))
	}

	if mockClient.lastReq == nil {
		t.Fatal("Expected gRPC request to be made")
	}

	if len(mockClient.lastReq.Weather) != 24 {
		t.Errorf("Expected 24 weather data points, got %d", len(mockClient.lastReq.Weather))
	}
}

func TestSolve(t *testing.T) {
	mockClient := &mockSolarSolverClient{}
	service := NewSimulationService(mockClient)

	params := SolveParams{
		Panel:            &SolarPanel{Pdc0: 300},
		Inverter:         &SolarInverter{Pdc0: 5000},
		ModulesPerString: 10,
		Strings:          2,
		Duration:         2 * time.Hour,
		When:             time.Date(2026, 6, 21, 12, 0, 0, 0, time.UTC),
		Temperature:      25.0,
		Location:         &pb.Location{Latitude: 52.2},
	}

	res, err := service.Solve(context.Background(), params)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}

	if len(res.AcOutput) != 2 {
		t.Errorf("Expected 2 outputs, got %d", len(res.AcOutput))
	}

	if len(mockClient.lastReq.Weather) != 2 {
		t.Errorf("Expected 2 weather data points, got %d", len(mockClient.lastReq.Weather))
	}
}
