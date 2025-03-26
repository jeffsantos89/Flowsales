from fastapi import APIRouter
from services.linkedin_service import LinkedInService

router = APIRouter()

@router.post("/linkedin/message")
async def send_linkedin_message(user_id: str, message: str):
    response = LinkedInService.send_message(user_id, message)
    return {"status": response}
    @router.post("/linkedin/engage")
    async def automated_engagement(
        user_id: str,
        message_template: str,
        engagement_type: str,
        frequency: int = 1,
        max_interactions: int = 10
    ):
        """
        Handles automated LinkedIn engagement with configurable parameters.
        """
        try:
            response = LinkedInService.create_engagement_campaign(
                user_id=user_id,
                template=message_template,
                type=engagement_type,
                frequency=frequency,
                max_interactions=max_interactions
            )
            return {"status": "success", "campaign_id": response.get("id")}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @router.get("/linkedin/analytics/{campaign_id}")
    async def get_engagement_analytics(campaign_id: str):
        """
        Retrieves analytics for a specific engagement campaign.
        """
        try:
            analytics = LinkedInService.get_campaign_analytics(campaign_id)
            return analytics
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @router.put("/linkedin/campaign/{campaign_id}")
    async def update_campaign(campaign_id: str, status: str):
        """
        Updates the status of an engagement campaign.
        """
        try:
            result = LinkedInService.update_campaign_status(campaign_id, status)
            return {"status": "success", "updated": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}