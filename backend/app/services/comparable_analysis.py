"""
Comparable Company Analysis System

This module provides comprehensive peer company analysis including:
- Peer company identification algorithms
- Valuation multiples calculation (P/E, P/B, P/S, EV/EBITDA)
- Financial metrics benchmarking
- Industry analysis and trends
- Peer ranking and scoring systems
- Relative valuation analysis
- Statistical analysis and validation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import math
from scipy import stats
import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


@dataclass
class PeerCompany:
    """Peer Company Data Structure"""
    symbol: str
    name: str
    market_cap: float
    enterprise_value: float
    revenue: float
    ebitda: float
    net_income: float
    shares_outstanding: float
    price: float
    pe: float
    pb: float
    ps: float
    ev_revenue: float
    ev_ebitda: float
    peg: float
    roe: float
    roa: float
    debt_to_equity: float
    current_ratio: float
    industry: str
    sector: str
    market_cap_category: str  # Large, Mid, Small


@dataclass
class ValuationMetric:
    """Valuation Metric Statistics"""
    min: float
    max: float
    median: float
    mean: float
    percentile_25: float
    percentile_75: float
    standard_deviation: float
    count: int


@dataclass
class ComparableValuation:
    """Comparable Valuation Results"""
    pe_based: float
    pb_based: float
    ps_based: float
    ev_revenue_based: float
    ev_ebitda_based: float
    average: float
    median: float
    weighted_average: float
    confidence_score: float


@dataclass
class PeerRanking:
    """Peer Company Ranking"""
    symbol: str
    name: str
    overall_score: float
    valuation_score: float
    profitability_score: float
    growth_score: float
    financial_health_score: float
    rank: int


class PeerIdentificationEngine:
    """Peer Company Identification Engine"""
    
    def __init__(self):
        pass
    
    def identify_peers(self, target_company: Dict[str, Any], universe: List[Dict[str, Any]], 
                      criteria: Dict[str, Any]) -> List[PeerCompany]:
        """Identify peer companies based on multiple criteria"""
        try:
            peers = []
            
            for company in universe:
                # Skip the target company itself
                if company.get('symbol') == target_company.get('symbol'):
                    continue
                
                # Apply filtering criteria
                if self._meets_criteria(company, target_company, criteria):
                    peer = self._create_peer_company(company)
                    if peer:
                        peers.append(peer)
            
            # Sort by relevance score
            peers.sort(key=lambda x: self._calculate_relevance_score(x, target_company), reverse=True)
            
            # Return top N peers
            max_peers = criteria.get('max_peers', 20)
            return peers[:max_peers]
            
        except Exception as e:
            logger.error(f"Peer identification failed: {e}")
            raise ValueError(f"Peer identification failed: {e}")
    
    def _meets_criteria(self, company: Dict[str, Any], target: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if company meets peer identification criteria"""
        try:
            # Industry/Sector match
            if criteria.get('require_industry_match', True):
                if company.get('industry') != target.get('industry'):
                    return False
            
            # Market cap range
            target_market_cap = target.get('market_cap', 0)
            company_market_cap = company.get('market_cap', 0)
            
            if target_market_cap > 0 and company_market_cap > 0:
                market_cap_ratio = company_market_cap / target_market_cap
                min_ratio = criteria.get('min_market_cap_ratio', 0.1)
                max_ratio = criteria.get('max_market_cap_ratio', 10.0)
                
                if not (min_ratio <= market_cap_ratio <= max_ratio):
                    return False
            
            # Geographic region (if specified)
            if criteria.get('require_region_match', False):
                if company.get('country') != target.get('country'):
                    return False
            
            # Exchange (if specified)
            if criteria.get('require_exchange_match', False):
                if company.get('exchange') != target.get('exchange'):
                    return False
            
            # Minimum data quality
            required_fields = ['revenue', 'market_cap', 'price']
            for field in required_fields:
                if not company.get(field) or company.get(field) <= 0:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Criteria check failed: {e}")
            return False
    
    def _create_peer_company(self, company_data: Dict[str, Any]) -> Optional[PeerCompany]:
        """Create PeerCompany object from raw data"""
        try:
            # Calculate valuation multiples
            market_cap = company_data.get('market_cap', 0)
            revenue = company_data.get('revenue', 0)
            ebitda = company_data.get('ebitda', 0)
            net_income = company_data.get('net_income', 0)
            shares_outstanding = company_data.get('shares_outstanding', 0)
            price = company_data.get('price', 0)
            total_debt = company_data.get('total_debt', 0)
            cash = company_data.get('cash', 0)
            book_value = company_data.get('book_value', 0)
            total_assets = company_data.get('total_assets', 0)
            total_equity = company_data.get('total_equity', 0)
            current_assets = company_data.get('current_assets', 0)
            current_liabilities = company_data.get('current_liabilities', 0)
            
            # Enterprise Value
            enterprise_value = market_cap + total_debt - cash
            
            # Valuation Multiples
            pe = market_cap / net_income if net_income > 0 else 0
            pb = market_cap / book_value if book_value > 0 else 0
            ps = market_cap / revenue if revenue > 0 else 0
            ev_revenue = enterprise_value / revenue if revenue > 0 else 0
            ev_ebitda = enterprise_value / ebitda if ebitda > 0 else 0
            
            # Growth rate (simplified - would need historical data)
            growth_rate = company_data.get('revenue_growth_rate', 0)
            peg = pe / (growth_rate * 100) if growth_rate > 0 and pe > 0 else 0
            
            # Profitability ratios
            roe = net_income / total_equity if total_equity > 0 else 0
            roa = net_income / total_assets if total_assets > 0 else 0
            
            # Financial health ratios
            debt_to_equity = total_debt / total_equity if total_equity > 0 else 0
            current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
            
            # Market cap category
            if market_cap >= 10_000_000_000:  # $10B+
                market_cap_category = "Large"
            elif market_cap >= 2_000_000_000:  # $2B+
                market_cap_category = "Mid"
            else:
                market_cap_category = "Small"
            
            return PeerCompany(
                symbol=company_data.get('symbol', ''),
                name=company_data.get('name', ''),
                market_cap=market_cap,
                enterprise_value=enterprise_value,
                revenue=revenue,
                ebitda=ebitda,
                net_income=net_income,
                shares_outstanding=shares_outstanding,
                price=price,
                pe=pe,
                pb=pb,
                ps=ps,
                ev_revenue=ev_revenue,
                ev_ebitda=ev_ebitda,
                peg=peg,
                roe=roe,
                roa=roa,
                debt_to_equity=debt_to_equity,
                current_ratio=current_ratio,
                industry=company_data.get('industry', ''),
                sector=company_data.get('sector', ''),
                market_cap_category=market_cap_category
            )
            
        except Exception as e:
            logger.error(f"Failed to create peer company: {e}")
            return None
    
    def _calculate_relevance_score(self, peer: PeerCompany, target: Dict[str, Any]) -> float:
        """Calculate relevance score for peer company"""
        try:
            score = 0.0
            
            # Industry match (highest weight)
            if peer.industry == target.get('industry'):
                score += 40
            
            # Market cap similarity
            target_market_cap = target.get('market_cap', 0)
            if target_market_cap > 0:
                market_cap_ratio = peer.market_cap / target_market_cap
                if 0.5 <= market_cap_ratio <= 2.0:  # Within 2x range
                    score += 30
                elif 0.25 <= market_cap_ratio <= 4.0:  # Within 4x range
                    score += 20
                elif 0.1 <= market_cap_ratio <= 10.0:  # Within 10x range
                    score += 10
            
            # Sector match
            if peer.sector == target.get('sector'):
                score += 20
            
            # Geographic proximity (if available)
            # This would require additional data
            
            # Business model similarity (if available)
            # This would require additional analysis
            
            return score
            
        except Exception as e:
            logger.error(f"Relevance score calculation failed: {e}")
            return 0.0


class ValuationMultiplesEngine:
    """Valuation Multiples Calculation Engine"""
    
    def __init__(self):
        pass
    
    def calculate_valuation_metrics(self, peers: List[PeerCompany]) -> Dict[str, ValuationMetric]:
        """Calculate comprehensive valuation metrics for peer group"""
        try:
            metrics = {}
            
            # Extract multiples data
            pe_values = [p.pe for p in peers if p.pe > 0 and p.pe < 100]  # Filter outliers
            pb_values = [p.pb for p in peers if p.pb > 0 and p.pb < 20]
            ps_values = [p.ps for p in peers if p.ps > 0 and p.ps < 50]
            ev_revenue_values = [p.ev_revenue for p in peers if p.ev_revenue > 0 and p.ev_revenue < 20]
            ev_ebitda_values = [p.ev_ebitda for p in peers if p.ev_ebitda > 0 and p.ev_ebitda < 50]
            
            # Calculate statistics for each multiple
            metrics['pe'] = self._calculate_metric_stats(pe_values)
            metrics['pb'] = self._calculate_metric_stats(pb_values)
            metrics['ps'] = self._calculate_metric_stats(ps_values)
            metrics['ev_revenue'] = self._calculate_metric_stats(ev_revenue_values)
            metrics['ev_ebitda'] = self._calculate_metric_stats(ev_ebitda_values)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Valuation metrics calculation failed: {e}")
            raise ValueError(f"Valuation metrics calculation failed: {e}")
    
    def _calculate_metric_stats(self, values: List[float]) -> ValuationMetric:
        """Calculate statistical metrics for a valuation multiple"""
        try:
            if not values:
                return ValuationMetric(0, 0, 0, 0, 0, 0, 0, 0)
            
            values_array = np.array(values)
            
            return ValuationMetric(
                min=float(np.min(values_array)),
                max=float(np.max(values_array)),
                median=float(np.median(values_array)),
                mean=float(np.mean(values_array)),
                percentile_25=float(np.percentile(values_array, 25)),
                percentile_75=float(np.percentile(values_array, 75)),
                standard_deviation=float(np.std(values_array)),
                count=len(values)
            )
            
        except Exception as e:
            logger.error(f"Metric stats calculation failed: {e}")
            return ValuationMetric(0, 0, 0, 0, 0, 0, 0, 0)


class ComparableValuationEngine:
    """Comparable Valuation Analysis Engine"""
    
    def __init__(self):
        self.peer_engine = PeerIdentificationEngine()
        self.multiples_engine = ValuationMultiplesEngine()
    
    def perform_comparable_analysis(self, target_company: Dict[str, Any], 
                                  peer_universe: List[Dict[str, Any]],
                                  target_financials: Dict[str, float]) -> Dict[str, Any]:
        """Perform comprehensive comparable company analysis"""
        try:
            # Identify peers
            criteria = {
                'require_industry_match': True,
                'min_market_cap_ratio': 0.1,
                'max_market_cap_ratio': 10.0,
                'max_peers': 20
            }
            
            peers = self.peer_engine.identify_peers(target_company, peer_universe, criteria)
            
            if len(peers) < 3:
                raise ValueError("Insufficient peer companies found for analysis")
            
            # Calculate valuation metrics
            valuation_metrics = self.multiples_engine.calculate_valuation_metrics(peers)
            
            # Perform relative valuation
            comparable_valuation = self._calculate_relative_valuation(target_financials, valuation_metrics)
            
            # Calculate peer rankings
            peer_rankings = self._calculate_peer_rankings(peers, target_company)
            
            # Industry analysis
            industry_analysis = self._analyze_industry_trends(peers)
            
            return {
                'target_company': target_company,
                'peers': [self._peer_to_dict(p) for p in peers],
                'valuation_metrics': {k: self._metric_to_dict(v) for k, v in valuation_metrics.items()},
                'comparable_valuation': self._valuation_to_dict(comparable_valuation),
                'peer_rankings': [self._ranking_to_dict(r) for r in peer_rankings],
                'industry_analysis': industry_analysis,
                'analysis_metadata': {
                    'peer_count': len(peers),
                    'analysis_date': datetime.now().isoformat(),
                    'confidence_score': comparable_valuation.confidence_score
                }
            }
            
        except Exception as e:
            logger.error(f"Comparable analysis failed: {e}")
            raise ValueError(f"Comparable analysis failed: {e}")
    
    def _calculate_relative_valuation(self, target_financials: Dict[str, float], 
                                    valuation_metrics: Dict[str, ValuationMetric]) -> ComparableValuation:
        """Calculate relative valuation based on peer multiples"""
        try:
            target_revenue = target_financials.get('revenue', 0)
            target_ebitda = target_financials.get('ebitda', 0)
            target_net_income = target_financials.get('net_income', 0)
            target_book_value = target_financials.get('book_value', 0)
            
            valuations = []
            weights = []
            
            # P/E based valuation
            if target_net_income > 0 and valuation_metrics['pe'].median > 0:
                pe_valuation = target_net_income * valuation_metrics['pe'].median
                valuations.append(pe_valuation)
                weights.append(0.3)  # Higher weight for P/E
            
            # P/B based valuation
            if target_book_value > 0 and valuation_metrics['pb'].median > 0:
                pb_valuation = target_book_value * valuation_metrics['pb'].median
                valuations.append(pb_valuation)
                weights.append(0.2)
            
            # P/S based valuation
            if target_revenue > 0 and valuation_metrics['ps'].median > 0:
                ps_valuation = target_revenue * valuation_metrics['ps'].median
                valuations.append(ps_valuation)
                weights.append(0.2)
            
            # EV/Revenue based valuation
            if target_revenue > 0 and valuation_metrics['ev_revenue'].median > 0:
                ev_revenue_valuation = target_revenue * valuation_metrics['ev_revenue'].median
                valuations.append(ev_revenue_valuation)
                weights.append(0.15)
            
            # EV/EBITDA based valuation
            if target_ebitda > 0 and valuation_metrics['ev_ebitda'].median > 0:
                ev_ebitda_valuation = target_ebitda * valuation_metrics['ev_ebitda'].median
                valuations.append(ev_ebitda_valuation)
                weights.append(0.15)
            
            if not valuations:
                raise ValueError("No valid valuation multiples available")
            
            # Calculate weighted average
            total_weight = sum(weights)
            weighted_avg = sum(v * w for v, w in zip(valuations, weights)) / total_weight if total_weight > 0 else 0
            
            # Calculate confidence score based on data quality and consistency
            confidence_score = self._calculate_confidence_score(valuations, valuation_metrics)
            
            return ComparableValuation(
                pe_based=valuations[0] if len(valuations) > 0 else 0,
                pb_based=valuations[1] if len(valuations) > 1 else 0,
                ps_based=valuations[2] if len(valuations) > 2 else 0,
                ev_revenue_based=valuations[3] if len(valuations) > 3 else 0,
                ev_ebitda_based=valuations[4] if len(valuations) > 4 else 0,
                average=sum(valuations) / len(valuations),
                median=np.median(valuations),
                weighted_average=weighted_avg,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Relative valuation calculation failed: {e}")
            raise ValueError(f"Relative valuation calculation failed: {e}")
    
    def _calculate_confidence_score(self, valuations: List[float], 
                                  valuation_metrics: Dict[str, ValuationMetric]) -> float:
        """Calculate confidence score for the valuation"""
        try:
            if not valuations:
                return 0.0
            
            # Base score from number of multiples used
            base_score = min(len(valuations) * 20, 100)
            
            # Consistency score (lower standard deviation = higher confidence)
            if len(valuations) > 1:
                std_dev = np.std(valuations)
                mean_val = np.mean(valuations)
                coefficient_of_variation = std_dev / mean_val if mean_val > 0 else 1
                consistency_score = max(0, 30 * (1 - coefficient_of_variation))
            else:
                consistency_score = 0
            
            # Data quality score
            quality_score = 0
            for metric_name, metric in valuation_metrics.items():
                if metric.count >= 5:  # At least 5 peers
                    quality_score += 10
            
            total_score = base_score + consistency_score + quality_score
            return min(100, max(0, total_score))
            
        except Exception as e:
            logger.error(f"Confidence score calculation failed: {e}")
            return 0.0
    
    def _calculate_peer_rankings(self, peers: List[PeerCompany], target: Dict[str, Any]) -> List[PeerRanking]:
        """Calculate peer company rankings"""
        try:
            rankings = []
            
            for peer in peers:
                # Valuation score (lower multiples = better)
                valuation_score = 100 - min(100, (peer.pe + peer.pb + peer.ps) / 3 * 10)
                
                # Profitability score
                profitability_score = (peer.roe + peer.roa) * 10
                profitability_score = min(100, max(0, profitability_score))
                
                # Growth score (simplified - would need historical data)
                growth_score = 50  # Placeholder
                
                # Financial health score
                health_score = 100 - min(100, peer.debt_to_equity * 20)
                health_score = max(0, health_score)
                
                # Overall score (weighted average)
                overall_score = (
                    valuation_score * 0.3 +
                    profitability_score * 0.3 +
                    growth_score * 0.2 +
                    health_score * 0.2
                )
                
                rankings.append(PeerRanking(
                    symbol=peer.symbol,
                    name=peer.name,
                    overall_score=round(overall_score, 2),
                    valuation_score=round(valuation_score, 2),
                    profitability_score=round(profitability_score, 2),
                    growth_score=round(growth_score, 2),
                    financial_health_score=round(health_score, 2),
                    rank=0  # Will be set after sorting
                ))
            
            # Sort by overall score and assign ranks
            rankings.sort(key=lambda x: x.overall_score, reverse=True)
            for i, ranking in enumerate(rankings):
                ranking.rank = i + 1
            
            return rankings
            
        except Exception as e:
            logger.error(f"Peer ranking calculation failed: {e}")
            return []
    
    def _analyze_industry_trends(self, peers: List[PeerCompany]) -> Dict[str, Any]:
        """Analyze industry trends from peer data"""
        try:
            if not peers:
                return {}
            
            # Calculate industry averages
            avg_pe = np.mean([p.pe for p in peers if p.pe > 0])
            avg_pb = np.mean([p.pb for p in peers if p.pb > 0])
            avg_roe = np.mean([p.roe for p in peers if p.roe > 0])
            avg_debt_equity = np.mean([p.debt_to_equity for p in peers if p.debt_to_equity > 0])
            
            # Market cap distribution
            large_cap_count = sum(1 for p in peers if p.market_cap_category == "Large")
            mid_cap_count = sum(1 for p in peers if p.market_cap_category == "Mid")
            small_cap_count = sum(1 for p in peers if p.market_cap_category == "Small")
            
            return {
                'average_pe': round(avg_pe, 2),
                'average_pb': round(avg_pb, 2),
                'average_roe': round(avg_roe, 2),
                'average_debt_to_equity': round(avg_debt_equity, 2),
                'market_cap_distribution': {
                    'large_cap': large_cap_count,
                    'mid_cap': mid_cap_count,
                    'small_cap': small_cap_count
                },
                'peer_count': len(peers)
            }
            
        except Exception as e:
            logger.error(f"Industry trends analysis failed: {e}")
            return {}
    
    def _peer_to_dict(self, peer: PeerCompany) -> Dict[str, Any]:
        """Convert PeerCompany to dictionary"""
        return {
            'symbol': peer.symbol,
            'name': peer.name,
            'market_cap': peer.market_cap,
            'enterprise_value': peer.enterprise_value,
            'revenue': peer.revenue,
            'ebitda': peer.ebitda,
            'net_income': peer.net_income,
            'shares_outstanding': peer.shares_outstanding,
            'price': peer.price,
            'pe': peer.pe,
            'pb': peer.pb,
            'ps': peer.ps,
            'ev_revenue': peer.ev_revenue,
            'ev_ebitda': peer.ev_ebitda,
            'peg': peer.peg,
            'roe': peer.roe,
            'roa': peer.roa,
            'debt_to_equity': peer.debt_to_equity,
            'current_ratio': peer.current_ratio,
            'industry': peer.industry,
            'sector': peer.sector,
            'market_cap_category': peer.market_cap_category
        }
    
    def _metric_to_dict(self, metric: ValuationMetric) -> Dict[str, Any]:
        """Convert ValuationMetric to dictionary"""
        return {
            'min': metric.min,
            'max': metric.max,
            'median': metric.median,
            'mean': metric.mean,
            'percentile_25': metric.percentile_25,
            'percentile_75': metric.percentile_75,
            'standard_deviation': metric.standard_deviation,
            'count': metric.count
        }
    
    def _valuation_to_dict(self, valuation: ComparableValuation) -> Dict[str, Any]:
        """Convert ComparableValuation to dictionary"""
        return {
            'pe_based': valuation.pe_based,
            'pb_based': valuation.pb_based,
            'ps_based': valuation.ps_based,
            'ev_revenue_based': valuation.ev_revenue_based,
            'ev_ebitda_based': valuation.ev_ebitda_based,
            'average': valuation.average,
            'median': valuation.median,
            'weighted_average': valuation.weighted_average,
            'confidence_score': valuation.confidence_score
        }
    
    def _ranking_to_dict(self, ranking: PeerRanking) -> Dict[str, Any]:
        """Convert PeerRanking to dictionary"""
        return {
            'symbol': ranking.symbol,
            'name': ranking.name,
            'overall_score': ranking.overall_score,
            'valuation_score': ranking.valuation_score,
            'profitability_score': ranking.profitability_score,
            'growth_score': ranking.growth_score,
            'financial_health_score': ranking.financial_health_score,
            'rank': ranking.rank
        }
