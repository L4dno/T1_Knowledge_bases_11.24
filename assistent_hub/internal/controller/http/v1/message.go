package v1

import (
	"account-management-service/internal/service"
	"net/http"

	"github.com/labstack/echo/v4"
)

type messageRoutes struct {
	messageService service.Message
}

// function for struct Message routing
func newMessageRoutes(g *echo.Group, messageService service.Message) {
	r := &messageRoutes{
		messageService: messageService,
	}
	// creating endpoints for requests
	g.POST("/create", r.create)
	// here we should get all the messages by uid
	g.GET("/", r.getBalance)
}

// @Summary Create message
// @Description Create message
// @Tags messages
// @Accept json
// @Produce json
// @Success 201 {object} v1.messageRoutes.create.response
// @Failure 400 {object} echo.HTTPError
// @Failure 500 {object} echo.HTTPError
// @Security JWT
// @Router /api/v1/messages/create [post]
func (r *messageRoutes) create(c echo.Context) error {
	id, err := r.messageService.CreateMessage(c.Request().Context())
	if err != nil {
		if err == service.ErrMessageAlreadyExists {
			newErrorResponse(c, http.StatusBadRequest, err.Error())
			return err
		}
		newErrorResponse(c, http.StatusInternalServerError, "internal server error")
		return err
	}

	type response struct {
		Id int `json:"id"`
	}

	return c.JSON(http.StatusCreated, response{
		Id: id,
	})
}

// here we get messages by uid
type getBalanceInput struct {
	Id int `json:"id" validate:"required"`
}

// @Summary Get massage
// @Description Get massage
// @Tags messages
// @Accept json
// @Produce json
// @Param input body v1.getMassageInput true "input"
// @Success 200 {object} v1.messageRoutes.getMessage.response
// @Failure 400 {object} echo.HTTPError
// @Failure 500 {object} echo.HTTPError
// @Security JWT
// @Router /api/v1/messages/ [get]
func (r *messageRoutes) getBalance(c echo.Context) error {
	var input getBalanceInput

	if err := c.Bind(&input); err != nil {
		newErrorResponse(c, http.StatusBadRequest, "invalid request body")
		return err
	}

	if err := c.Validate(input); err != nil {
		newErrorResponse(c, http.StatusBadRequest, err.Error())
		return err
	}

	message, err := r.messageService.GetMessageById(c.Request().Context(), input.Id)
	if err != nil {
		if err == service.ErrMessageNotFound {
			newErrorResponse(c, http.StatusBadRequest, err.Error())
			return err
		}
		newErrorResponse(c, http.StatusInternalServerError, "internal server error")
		return err
	}

	type response struct {
		Uid    int    `json:"id"`
		Prompt string `json:"prompt"`
	}

	return c.JSON(http.StatusOK, response{
		Uid:    message.Uid,
		Prompt: message.Prompt,
	})
}
