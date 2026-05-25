package uldk

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

// Client handles communication with the ULDK (Usługa Lokalizacji Działek Katastralnych) service.
type Client struct {
	httpClient *http.Client
	baseURL    string
}

// NewClient creates a new ULDK client.
func NewClient() *Client {
	return &Client{
		httpClient: &http.Client{Timeout: 10 * time.Second},
		baseURL:    "https://uldk.gugik.gov.pl/",
	}
}

// do executes an HTTP request and performs basic status check.
func (c *Client) do(ctx context.Context, url string) (io.ReadCloser, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		return nil, fmt.Errorf("uldk api error: status %d", resp.StatusCode)
	}

	return resp.Body, nil
}

// parseResponse reads the standard ULDK response format:
// Line 1: Status code (0 for success, -1 for no results, >0 for error)
// Line 2: Result data (optional)
func (c *Client) parseResponse(r io.Reader) (string, error) {
	scanner := bufio.NewScanner(r)
	if !scanner.Scan() {
		return "", fmt.Errorf("empty response from uldk")
	}

	statusLine := strings.TrimSpace(scanner.Text())
	if statusLine == "-1" {
		return "", fmt.Errorf("no results found")
	}

	var statusCode int
	if _, err := fmt.Sscanf(statusLine, "%d", &statusCode); err != nil {
		return "", fmt.Errorf("invalid status code from uldk: %s", statusLine)
	}

	if statusCode != 0 {
		message := "ULDK service returned error"
		if scanner.Scan() {
			message = scanner.Text()
		}
		return "", &ULDKError{Code: statusCode, Message: message}
	}

	if !scanner.Scan() {
		return "", nil
	}

	return scanner.Text(), nil
}
