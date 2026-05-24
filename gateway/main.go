package main

import (
	"log"
	"net/http"

	"github.com/hubertkuch/solar/gateway/internal/simulation"
	"github.com/hubertkuch/solar/gateway/internal/weather"
	pb "github.com/hubertkuch/solar/gateway/pb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func main() {
	conn, err := grpc.NewClient("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()

	grpcClient := pb.NewSolarSolverClient(conn)

	// Dependency Injection
	weatherProvider := weather.NewOpenMeteoProvider()
	simService := simulation.NewSimulationService(grpcClient, weatherProvider)
	simHandler := simulation.NewSimulationHandler(simService)

	mux := http.NewServeMux()
	mux.HandleFunc("/api/simulation", simHandler.HandleSimulation)
	mux.HandleFunc("/api/solve", simHandler.HandleSolve)

	port := ":8085"
	log.Printf("Gateway HTTP server starting on %s...", port)
	if err := http.ListenAndServe(port, mux); err != nil {
		log.Fatalf("HTTP server failed: %v", err)
	}
}
