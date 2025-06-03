package main

import (
	"crypto/tls"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/go-gomail/gomail"
	"github.com/joho/godotenv"
)

type EmailData struct {
	Subject     string   `json:"subject"`
	Message     string   `json:"message"`
	Recipient   []string `json:"recipient"`
	HTMLMessage string   `json:"html_message"`
	Attachments []string `json:"attachments"`
	Images      []string `json:"images"`
}

var (
	EMAIL_HOST          = ""
	EMAIL_PORT          = 0
	EMAIL_USE_SSL       = false
	EMAIL_HOST_USER     = ""
	EMAIL_HOST_PASSWORD = ""
)

func init() {
	if err := godotenv.Load("../.env"); err != nil {
		log.Fatal("Error loading .env file")
	}

	EMAIL_HOST = os.Getenv("EMAIL_HOST")
	EMAIL_PORT = mustAtoi(os.Getenv("EMAIL_PORT"))
	EMAIL_USE_SSL = os.Getenv("EMAIL_USE_SSL") == "True"
	EMAIL_HOST_USER = os.Getenv("EMAIL_HOST_USER")
	EMAIL_HOST_PASSWORD = os.Getenv("EMAIL_HOST_PASSWORD")
}

func sendEmail(data *EmailData) error {
	m := gomail.NewMessage()
	m.SetHeader("From", EMAIL_HOST_USER)
	m.SetHeader("To", data.Recipient...)
	m.SetHeader("Subject", data.Subject)
	m.SetBody("text/plain", data.Message)

	if data.HTMLMessage != "" {
		m.AddAlternative("text/html", data.HTMLMessage)
	}

	for _, attachment := range data.Attachments {
		f, err := os.Open(attachment)
		if err != nil {
			continue
		}
		f.Close()

		m.Attach(attachment)
	}

	for _, image := range data.Images {
		f, err := os.Open(image)
		if err != nil {
			continue
		}
		f.Close()

		m.Embed(image)
	}

	d := gomail.NewDialer(EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
	if EMAIL_USE_SSL {
		d.SSL = true
	} else {
		d.TLSConfig = &tls.Config{InsecureSkipVerify: true}
	}

	if err := d.DialAndSend(m); err != nil {
		return err
	}

	return nil
}

func mustAtoi(s string) int {
	i, err := strconv.Atoi(s)
	if err != nil {
		panic(err)
	}
	return i
}

func validate(data *EmailData) error {
	if data.Subject == "" || data.Message == "" || len(data.Recipient) == 0 {
		return errors.New("subject, message, and recipient are required")
	}

	return nil
}

func getFiles(r *http.Request, key string) []string {
	var files []string
	m := r.MultipartForm
	if m != nil && len(m.File[key]) > 0 {
		for _, f := range m.File[key] {
			files = append(files, f.Filename)
		}
	}

	return files
}

func getDataFromPostForm(r *http.Request) (*EmailData, error) {
	data := &EmailData{}

	if err := r.ParseForm(); err != nil {
		return nil, err
	}

	data.Subject = r.PostFormValue("subject")
	data.Message = r.PostFormValue("message")
	data.Recipient = r.PostForm["recipient"]
	data.HTMLMessage = r.PostFormValue("html_message")

	return data, nil
}

func getDataFromForm(r *http.Request) (*EmailData, error) {
	data := &EmailData{}

	if err := r.ParseForm(); err != nil {
		return nil, err
	}

	if r.Form == nil || r.FormValue("subject") == "" {
		return getDataFromPostForm(r)
	}

	data.Subject = r.FormValue("subject")
	data.Message = r.FormValue("message")
	data.Recipient = r.Form["recipient"]
	data.Images = getFiles(r, "images")
	data.Attachments = getFiles(r, "attachments")

	return data, nil
}

func getDataFromMultiPartForm(r *http.Request) (*EmailData, error) {
	if err := r.ParseMultipartForm(32 << 20); err != nil {
		return nil, err
	}

	if r.MultipartForm == nil || len(r.MultipartForm.Value["subject"]) == 0 {
		return getDataFromForm(r)
	}

	data := &EmailData{}
	data.Subject = r.FormValue("subject")
	data.Message = r.FormValue("message")
	data.Recipient = r.MultipartForm.Value["recipient"]
	data.HTMLMessage = r.FormValue("html_message")
	data.Images = getFiles(r, "images")
	data.Attachments = getFiles(r, "attachments")

	return data, nil
}

func getData(r *http.Request) (*EmailData, error) {
	if strings.Contains(r.Header.Get("Content-Type"), "multipart/form-data") {
		return getDataFromMultiPartForm(r)
	}

	data := &EmailData{}
	err := json.NewDecoder(r.Body).Decode(data)
	if err != nil {
		return nil, err
	}

	if data.Subject == "" {
		return getDataFromMultiPartForm(r)
	}

	return data, nil
}

func handler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	data, err := getData(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if err := validate(data); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	err = sendEmail(data)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	log.Printf("Time taken to send email: %v\n", time.Since(start))
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"message": "OK"}`))
}

func main() {
	fmt.Println("Mail system starting at http://localhost:8443")
	http.HandleFunc("/send_email", handler)
	log.Fatal(http.ListenAndServe(":8443", nil))
}
