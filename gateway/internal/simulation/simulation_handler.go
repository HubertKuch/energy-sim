package simulation

import (
	"context"
	"encoding/json"
	"log/slog"
	"net/http"
	"time"
)

// SimulationHandler handles HTTP requests related to simulations.
type SimulationHandler struct {
	service SimulationService
	logger  *slog.Logger
}

// NewSimulationHandler creates a new SimulationHandler.
func NewSimulationHandler(service SimulationService, logger *slog.Logger) *SimulationHandler {
	return &SimulationHandler{
		service: service,
		logger:  logger,
	}
}

type errorResponse struct {
	Error string `json:"error"`
}

func (h *SimulationHandler) sendError(w http.ResponseWriter, message string, code int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(errorResponse{Error: message})
}

// HandleSimulation handles the POST /api/simulation request.
func (h *SimulationHandler) HandleSimulation(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		h.sendError(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req SimulationRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.logger.Warn("Failed to decode request body", "error", err)
		h.sendError(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), time.Second*30)
	defer cancel()

	res, err := h.service.RunSimulation(ctx, &req)
	if err != nil {
		h.logger.Error("Simulation failed", "error", err)
		h.sendError(w, err.Error(), http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(res); err != nil {
		h.logger.Error("Failed to encode response", "error", err)
	}
}

// HandleSolve handles the POST /api/solve request.
func (h *SimulationHandler) HandleSolve(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		h.sendError(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req SolveRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.logger.Warn("Failed to decode solve request body", "error", err)
		h.sendError(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	duration, err := time.ParseDuration(req.Duration)
	if err != nil {
		h.sendError(w, "Invalid duration", http.StatusBadRequest)
		return
	}

	when, err := time.Parse(time.RFC3339, req.When)
	if err != nil {
		h.sendError(w, "Invalid timestamp (RFC3339)", http.StatusBadRequest)
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), time.Second*30)
	defer cancel()

	params := SolveParams{
		Arrays:        req.Arrays,
		Inverter:      req.Inverter,
		Battery:       req.Battery,
		Duration:      duration,
		When:          when,
		Temperature:   req.Temperature,
		SnowDepthCm:   req.SnowDepthCm,
		Location:      req.Location,
		LoadProfileKw: req.LoadProfileKw,
	}

	weatherData, err := h.service.GetWeather(ctx, params)
	if err != nil {
		h.logger.Error("Failed to prepare weather data", "error", err)
		h.sendError(w, "Failed to prepare weather data", http.StatusInternalServerError)
		return
	}

	res, err := h.service.Solve(ctx, params, weatherData)
	if err != nil {
		h.logger.Error("Solve failed", "error", err)
		h.sendError(w, err.Error(), http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(res); err != nil {
		h.logger.Error("Failed to encode solve response", "error", err)
	}
}

