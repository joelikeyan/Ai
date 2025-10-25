#include "InteractionComponent.h"
#include "GameFramework/Character.h"
#include "Engine/World.h"
#include "DrawDebugHelpers.h"
#include "CoffeeMachine.h"

UInteractionComponent::UInteractionComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    CurrentInteractionTarget = nullptr;
}

void UInteractionComponent::BeginPlay()
{
    Super::BeginPlay();
}

void UInteractionComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    
    FindNearestInteractable();
}

void UInteractionComponent::Interact()
{
    if (CurrentInteractionTarget)
    {
        OnInteractionStarted.Broadcast(CurrentInteractionTarget);
        
        // Try to interact with coffee machine
        if (ACoffeeMachine* CoffeeMachine = Cast<ACoffeeMachine>(CurrentInteractionTarget))
        {
            // This will be handled by the coffee machine's interaction system
            // The actual interaction logic will be in Blueprint or additional C++ code
        }
        
        OnInteractionEnded.Broadcast(CurrentInteractionTarget);
    }
}

void UInteractionComponent::SetInteractionTarget(AActor* Target)
{
    UpdateInteractionTarget(Target);
}

void UInteractionComponent::ClearInteractionTarget()
{
    UpdateInteractionTarget(nullptr);
}

void UInteractionComponent::FindNearestInteractable()
{
    ACharacter* Owner = Cast<ACharacter>(GetOwner());
    if (!Owner)
        return;

    FVector OwnerLocation = Owner->GetActorLocation();
    FVector OwnerForward = Owner->GetActorForwardVector();
    
    TArray<FHitResult> HitResults;
    FCollisionQueryParams QueryParams;
    QueryParams.AddIgnoredActor(Owner);
    
    bool bHit = GetWorld()->SweepMultiByChannel(
        HitResults,
        OwnerLocation,
        OwnerLocation + (OwnerForward * InteractionRange),
        FQuat::Identity,
        ECC_WorldStatic,
        FCollisionShape::MakeSphere(50.0f),
        QueryParams
    );

    AActor* NearestInteractable = nullptr;
    float NearestDistance = InteractionRange;

    for (const FHitResult& Hit : HitResults)
    {
        AActor* HitActor = Hit.GetActor();
        if (HitActor && HitActor->IsA<ACoffeeMachine>())
        {
            float Distance = FVector::Dist(OwnerLocation, HitActor->GetActorLocation());
            if (Distance < NearestDistance)
            {
                NearestInteractable = HitActor;
                NearestDistance = Distance;
            }
        }
    }

    UpdateInteractionTarget(NearestInteractable);

    // Debug visualization
    if (bShowDebugInfo)
    {
        FColor DebugColor = CurrentInteractionTarget ? FColor::Green : FColor::Red;
        DrawDebugLine(GetWorld(), OwnerLocation, OwnerLocation + (OwnerForward * InteractionRange), DebugColor);
        DrawDebugSphere(GetWorld(), OwnerLocation + (OwnerForward * InteractionRange), 50.0f, 8, DebugColor);
    }
}

void UInteractionComponent::UpdateInteractionTarget(AActor* NewTarget)
{
    if (CurrentInteractionTarget != NewTarget)
    {
        CurrentInteractionTarget = NewTarget;
    }
}