package simulation

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"time"
)

// SimulationHandler handles HTTP requests related to simulations.
type SimulationHandler struct {
	service SimulationService
}

// NewSimulationHandler creates a new SimulationHandler.
func NewSimulationHandler(service SimulationService) *SimulationHandler {
	return &SimulationHandler{
		service: service,
	}
}

// HandleSimulation handles the POST /api/simulation request.
func (h *SimulationHandler) HandleSimulation(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req SimulationRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		log.Printf("Decode error: %v", err)
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), time.Second*30)
	defer cancel()

	res, err := h.service.RunSimulation(ctx, &req)
	if err != nil {
		log.Printf("Simulation error: %v", err)
		// Simple error check for validation failures
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(res); err != nil {
		log.Printf("Encode error: %v", err)
	}
}

// HandleSolve handles the POST /api/solve request.
func (h *SimulationHandler) HandleSolve(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req SolveRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		log.Printf("Decode error: %v", err)
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	duration, err := time.ParseDuration(req.Duration)
	if err != nil {
		http.Error(w, "Invalid duration", http.StatusBadRequest)
		return
	}

	when, err := time.Parse(time.RFC3339, req.When)
	if err != nil {
		http.Error(w, "Invalid timestamp (RFC3339)", http.StatusBadRequest)
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), time.Second*30)
	defer cancel()

	res, err := h.service.Solve(ctx, SolveParams{
		Arrays:        req.Arrays,
		Inverter:      req.Inverter,
		Battery:       req.Battery,
		Duration:      duration,
		When:          when,
		Temperature:   req.Temperature,
		Location:      req.Location,
		LoadProfileKw: req.LoadProfileKw,
	})
	if err != nil {
		log.Printf("Solve error: %v", err)
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(res); err != nil {
		log.Printf("Encode error: %v", err)
	}
}
