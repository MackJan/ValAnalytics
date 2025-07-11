import asyncio
import logging
from datetime import datetime, timedelta
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .database import engine
from .models import ActiveMatch

logger = logging.getLogger(__name__)

class MatchCleanupService:
    def __init__(self, cleanup_interval_minutes: int = 0.5, match_timeout_minutes: int = 1):
        """
        Initialize the cleanup service.

        Args:
            cleanup_interval_minutes: How often to run the cleanup (default: 5 minutes)
            match_timeout_minutes: How long to wait without updates before marking a match as stale (default: 10 minutes)
        """
        self.cleanup_interval = cleanup_interval_minutes * 60  # Convert to seconds
        self.match_timeout = match_timeout_minutes * 60  # Convert to seconds
        self.running = False
        self.task = None

    async def cleanup_stale_matches(self):
        """Clean up matches that haven't received updates within the timeout period"""
        try:
            async with AsyncSession(engine) as session:
                # Calculate the cutoff time
                cutoff_time = datetime.now() - timedelta(seconds=self.match_timeout)

                # Find active matches that haven't been updated recently
                query = select(ActiveMatch).where(
                    ActiveMatch.last_updated < cutoff_time  # Haven't been updated recently
                )

                result = await session.exec(query)
                stale_matches = result.all()

                if stale_matches:
                    logger.info(f"Found {len(stale_matches)} stale matches to clean up")

                    # Mark stale matches as ended
                    for match in stale_matches:
                        match.ended_at = datetime.now()
                        session.add(match)
                        logger.info(f"Marked match {match.match_uuid} as ended due to inactivity")

                    await session.commit()
                    logger.info(f"Successfully cleaned up {len(stale_matches)} stale matches")
                else:
                    logger.debug("No stale matches found during cleanup")

        except Exception as e:
            logger.error(f"Error during match cleanup: {str(e)}")

    async def _cleanup_loop(self):
        """Background loop that runs the cleanup periodically"""
        logger.info(f"Match cleanup service started (interval: {self.cleanup_interval}s, timeout: {self.match_timeout}s)")

        while self.running:
            try:
                await self.cleanup_stale_matches()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                logger.info("Match cleanup service cancelled")
                break
            except Exception as e:
                logger.error(f"Unexpected error in cleanup loop: {str(e)}")
                await asyncio.sleep(self.cleanup_interval)

    def start(self):
        """Start the background cleanup service"""
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self._cleanup_loop())
            logger.info("Match cleanup service started")

    async def stop(self):
        """Stop the background cleanup service"""
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
            logger.info("Match cleanup service stopped")

    async def update_match_activity(self, match_uuid: str):
        """Update the last_update timestamp for a specific match"""
        try:
            async with AsyncSession(engine) as session:
                query = select(ActiveMatch).where(
                    ActiveMatch.match_uuid == match_uuid,
                    ActiveMatch.ended_at.is_(None)
                )
                result = await session.exec(query)
                match = result.first()

                if match:
                    match.last_updated = datetime.now()
                    session.add(match)
                    await session.commit()
                    logger.debug(f"Updated activity timestamp for match {match_uuid}")
                else:
                    logger.warning(f"Could not find active match {match_uuid} to update activity")

        except Exception as e:
            logger.error(f"Error updating match activity for {match_uuid}: {str(e)}")

# Global instance
cleanup_service = MatchCleanupService()
