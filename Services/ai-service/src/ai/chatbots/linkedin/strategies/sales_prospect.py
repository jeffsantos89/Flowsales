"""
sales_prospect.py
Strategy for handling sales prospecting on LinkedIn (intent 'sales').
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from base import BaseLinkedInStrategy
from utils.logger import logger
from ai.exceptions import ProspectingError
from ai.models.prospect import ProspectProfile
from ai.services.analytics import AnalyticsService
from ai.services.crm import CRMService
from ai.utils.validators import LinkedInValidator

class ProspectStage(Enum):
    INITIAL_CONTACT = "initial_contact"
    INTERESTED = "interested"
    MEETING_REQUESTED = "meeting_requested"
    MEETING_SCHEDULED = "meeting_scheduled"
    FOLLOW_UP = "follow_up"

@dataclass
class SalesResponse:
    message: str
    response_type: str
    conversation_state: str
    next_action: Optional[str] = None
    meeting_slots: Optional[List[datetime]] = None
    prospect_score: Optional[float] = None

class SalesProspectStrategy(BaseLinkedInStrategy):
    """
    Handles sales prospecting, whether the user is inquiring about a product/service
    or if the company is initiating commercial contact.
    """

    def __init__(self):
        self.validator = LinkedInValidator()
        self.analytics = AnalyticsService()
        self.crm = CRMService()
        self.response_templates = self._load_response_templates()

    async def execute(
        self, 
        user_id: str, 
        message_text: str, 
        conversation: Dict[str, Any], 
        query_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the sales prospecting strategy.
        
        Args:
            user_id: LinkedIn user identifier
            message_text: The message received from the user
            conversation: Current conversation context
            query_info: Additional query information
            
        Returns:
            Dict containing the response and next actions
        
        Raises:
            ProspectingError: If there's an error during prospecting
        """
        try:
            logger.info(f"[SalesProspectStrategy] Processing sales prospect for user_id={user_id}")
            
            # Validate inputs
            self.validator.validate_message(message_text)
            
            # Analyze prospect profile
            prospect = await self._analyze_prospect(user_id)
            
            # Determine conversation stage
            current_stage = self._determine_stage(conversation)
            
            # Generate appropriate response
            response = await self._generate_response(prospect, current_stage, message_text)
            
            # Update CRM
            await self._update_crm(user_id, response, current_stage)
            
            # Track analytics
            self.analytics.track_interaction(user_id, current_stage, response)
            
            return response.__dict__

        except Exception as e:
            logger.error(f"Error in sales prospecting: {str(e)}", exc_info=True)
            raise ProspectingError(f"Failed to process sales prospect: {str(e)}")

    async def _analyze_prospect(self, user_id: str) -> ProspectProfile:
        """Analyze prospect profile and scoring."""
        # Implementation for prospect analysis
        profile = await self.crm.get_prospect_profile(user_id)
        return profile

    def _determine_stage(self, conversation: Dict[str, Any]) -> ProspectStage:
        """Determine the current stage of the sales conversation."""
        if not conversation.get("history"):
            return ProspectStage.INITIAL_CONTACT
        # Add logic to determine other stages
        return ProspectStage.FOLLOW_UP

    async def _generate_response(
        self,
        prospect: ProspectProfile,
        stage: ProspectStage,
        message: str
    ) -> SalesResponse:
        """Generate an appropriate response based on prospect and stage."""
        template = self.response_templates.get(stage, self.response_templates[ProspectStage.INITIAL_CONTACT])
        
        response = SalesResponse(
            message=template.format(prospect_name=prospect.name),
            response_type="sales_info",
            conversation_state=stage.value,
            prospect_score=prospect.score,
            next_action=self._determine_next_action(stage)
        )
        
        if stage == ProspectStage.INTERESTED:
            response.meeting_slots = await self._get_available_meeting_slots()
            
        return response

    def _load_response_templates(self) -> Dict[ProspectStage, str]:
        """Load response templates for different stages."""
        return {
            ProspectStage.INITIAL_CONTACT: "Olá {prospect_name}, percebi seu interesse em nossos serviços. "
                                         "Posso compartilhar mais informações sobre como podemos ajudar?",
            ProspectStage.INTERESTED: "Ótimo! Gostaria de agendar uma call para discutirmos mais detalhes?",
            # Add more templates for different stages
        }

    async def _update_crm(
        self,
        user_id: str,
        response: SalesResponse,
        stage: ProspectStage
    ) -> None:
        """Update CRM with interaction details."""
        await self.crm.update_interaction(
            user_id=user_id,
            stage=stage.value,
            response=response.message,
            timestamp=datetime.utcnow()
        )

    @staticmethod
    def _determine_next_action(stage: ProspectStage) -> str:
        """Determine the next action based on the current stage."""
        actions = {
            ProspectStage.INITIAL_CONTACT: "wait_for_response",
            ProspectStage.INTERESTED: "schedule_meeting",
            ProspectStage.MEETING_REQUESTED: "confirm_meeting",
        }
        return actions.get(stage, "follow_up")

    async def _get_available_meeting_slots(self) -> List[datetime]:
        """Get available meeting slots."""
        # Implementation for getting available meeting slots
        return []
