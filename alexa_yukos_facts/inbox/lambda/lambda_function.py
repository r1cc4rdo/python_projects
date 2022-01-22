# -*- coding: utf-8 -*-

import logging
from contextlib import suppress
from smtplib import SMTP_SSL as SMTP, SMTPException

import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def send_email(subject):

    email_from = 'your_user_name'
    email_to = 'add-to-things-##########@things.email'
    email_from_password = 'we_recommend_using_app_passwords'  # see: https://support.google.com/accounts/answer/185833
    message = '\r\n'.join([f'From: {email_from}', f'To: {email_to}', f'Subject: {subject}', '', ''])

    with suppress(SMTPException):
        with SMTP('smtp.gmail.com', 465) as smtp:
            smtp.login(f'{email_from}@gmail.com', email_from_password)
            smtp.sendmail(email_from, email_to, message)
        return True
    return False


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return (
            handler_input.response_builder
                .speak("This is Riccardo's inbox.")
                .ask("You can either add a task or say goodbye.")
                .response
        )


class AddTodoIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AddTodo")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        success = send_email(slots['todo_item'].value)
        return (
            handler_input.response_builder
                .speak(f'Done.' if success else 'Could not queue the task.')
                .ask("Do you want to add more? Add or bye.")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return (
            handler_input.response_builder
                .speak('You can either add a task or say goodbye.')
                .ask('Do you want to add more? Add or bye.')
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("MoreClose")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_request_type("SessionEndedRequest")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.speak('Ciao.').set_should_end_session(True).response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return (
            handler_input.response_builder
                .speak("You just triggered " + ask_utils.get_intent_name(handler_input) + ".")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        speak_output = "Sorry, I had trouble doing what you asked. Please try again."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AddTodoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(IntentReflectorHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
