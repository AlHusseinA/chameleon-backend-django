from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import Conversation
from api.service import call_dialogflow


class IntentionView(APIView):
    permission_classes = [AllowAny]
    # request response cycle ---> request is the object from axios on the frontend
    def post(self, request, *args, **kwargs):
        #data is a json from messageInput of two fields message and uuid
        chat_text = request.data['message']
        conversation_uuid = request.data['uuid']

        # get the session id, if it's not there then create it. (it will always use the same uuid received from the frontend)
        conversation, created = Conversation.objects.get_or_create(uuid=conversation_uuid, defaults={"messages": []})
        # here message and actor will accessed in the PreviousMessages component
        conversation.messages.append({"message": chat_text, "actor": "Me"})
        conversation.save()
        print(chat_text)
        returned_texts = call_dialogflow(conversation_uuid, texts=[chat_text])

        if returned_texts:
            new_message = returned_texts[0]
            narrator_message = returned_texts[0]
            conversation.messages.append({"message": new_message, "actor": "Chameleon"})

        conversation.save()
        print(conversation.messages)
        return Response(data=returned_texts, status=status.HTTP_200_OK)

# legacy, didn't actually use this since I relied on text to simulate events (clicking on buttons sends a pre-programmed text message to Chameleon)
class EventView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        event = request.data['event']
        returned_texts = call_dialogflow(event=event)
        return Response(data=returned_texts, status=status.HTTP_200_OK)


class PreviousMessagesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        conversation, _ = Conversation.objects.get_or_create(uuid=kwargs['conversation_uuid'], defaults={"messages": []})

        return Response(data=conversation.messages, status=status.HTTP_200_OK)
