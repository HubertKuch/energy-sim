package uldk

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGetParcelGeomByCoordinates(t *testing.T) {
	tests := []struct {
		name           string
		responseBody   string
		expectedID     string
		expectedWKB    string
		expectedError  bool
	}{
		{
			name: "success with ID and WKB",
			responseBody: "0\n141201_1.0001.1867/2|01030000208408000001000000080000009B0A892FA9161C4170C717D696211341",
			expectedID:   "141201_1.0001.1867/2",
			expectedWKB:  "01030000208408000001000000080000009B0A892FA9161C4170C717D696211341",
			expectedError: false,
		},
		{
			name: "success with WKB only (user sample)",
			responseBody: "0\n01030000208408000001000000080000009B0A892FA9161C4170C717D696211341",
			expectedID:   "",
			expectedWKB:  "01030000208408000001000000080000009B0A892FA9161C4170C717D696211341",
			expectedError: false,
		},
		{
			name: "no results (-1)",
			responseBody: "-1",
			expectedError: true,
		},
		{
			name: "uldk error code 1",
			responseBody: "1\nInvalid parameters",
			expectedError: true,
		},
		{
			name: "empty response",
			responseBody: "",
			expectedError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				fmt.Fprint(w, tt.responseBody)
			}))
			defer server.Close()

			client := NewClient()
			client.baseURL = server.URL + "/"

			resp, err := client.GetParcelGeomByCoordinates(context.Background(), ParcelRequest{X: 460166.4, Y: 313380.5})

			if tt.expectedError {
				if err == nil {
					t.Errorf("expected error, got nil")
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if resp.ParcelID != tt.expectedID {
				t.Errorf("expected ID %s, got %s", tt.expectedID, resp.ParcelID)
			}
			if resp.WKB != tt.expectedWKB {
				t.Errorf("expected WKB %s, got %s", tt.expectedWKB, resp.WKB)
			}
		})
	}
}
