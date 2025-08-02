package main

import (
	"encoding/json"
	"log"
	"net/http"
)

// Response is a simple structure for returning JSON
type Response struct {
	Message string `json:"message"`
}

// EchoRequest is the structure for incoming POST requests
type EchoRequest struct {
	Data string `json:"data"`
}

func main() {
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/hello", helloHandler)
	http.HandleFunc("/echo", echoHandler)

	log.Println("Starting server on :8080...")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatalf("Server failed: %s", err)
	}
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	jsonResponse(w, http.StatusOK, Response{Message: "Server is healthy!"})
}

func helloHandler(w http.ResponseWriter, r *http.Request) {
	jsonResponse(w, http.StatusOK, Response{Message: "Hello, World!"})
}

func echoHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		jsonResponse(w, http.StatusMethodNotAllowed, Response{Message: "Only POST is allowed"})
		return
	}

	var req EchoRequest
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		jsonResponse(w, http.StatusBadRequest, Response{Message: "Invalid JSON"})
		return
	}

	jsonResponse(w, http.StatusOK, Response{Message: "You said: " + req.Data})
}

func jsonResponse(w http.ResponseWriter, status int, resp Response) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(resp)
}
