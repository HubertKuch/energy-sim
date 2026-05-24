package main

import (
	"log/slog"
	"net/http"
	"os"
	"time"

	"github.com/hubertkuch/solar/gateway/internal/simulation"
	"github.com/hubertkuch/solar/gateway/internal/weather"
	pb "github.com/hubertkuch/solar/gateway/pb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func main() {
	// Initialize structured logger
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	slog.SetDefault(logger)

	conn, err := grpc.NewClient("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		logger.Error("did not connect", "error", err)
		os.Exit(1)
	}
	defer conn.Close()

	grpcClient := pb.NewSolarSolverClient(conn)

	// Dependency Injection
	weatherProvider := weather.NewOpenMeteoProvider()
	simService := simulation.NewSimulationService(grpcClient, weatherProvider)
	simHandler := simulation.NewSimulationHandler(simService, logger)

	mux := http.NewServeMux()
	mux.HandleFunc("/api/simulation", simHandler.HandleSimulation)
	mux.HandleFunc("/api/solve", simHandler.HandleSolve)

	port := ":8085"
	server := &http.Server{
		Addr:              port,
		Handler:           mux,
		ReadHeaderTimeout: 3 * time.Second,
		ReadTimeout:       5 * time.Second,
		WriteTimeout:      10 * time.Second,
		IdleTimeout:       120 * time.Second,
	}

	logger.Info("Gateway HTTP server starting", "port", port)
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		logger.Error("HTTP server failed", "error", err)
		os.Exit(1)
	}
}

