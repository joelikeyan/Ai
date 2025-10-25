#include "SimulationCharacter.h"
#include "Components/InputComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SphereComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/Engine.h"

ASimulationCharacter::ASimulationCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    // Create interaction component
    InteractionComponent = CreateDefaultSubobject<UInteractionComponent>(TEXT("InteractionComponent"));

    // Create grab mesh
    GrabMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("GrabMesh"));
    GrabMesh->SetupAttachment(RootComponent);
    GrabMesh->SetRelativeLocation(FVector(100.0f, 0.0f, 0.0f));
    GrabMesh->SetVisibility(false);

    // Create grab collision
    GrabCollision = CreateDefaultSubobject<USphereComponent>(TEXT("GrabCollision"));
    GrabCollision->SetupAttachment(RootComponent);
    GrabCollision->SetSphereRadius(150.0f);
    GrabCollision->SetRelativeLocation(FVector(100.0f, 0.0f, 0.0f));

    // Initialize variables
    GrabbedActor = nullptr;
}

void ASimulationCharacter::BeginPlay()
{
    Super::BeginPlay();
}

void ASimulationCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void ASimulationCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    // Bind interaction input
    PlayerInputComponent->BindAction(InteractActionName, IE_Pressed, this, &ASimulationCharacter::OnInteractPressed);
    PlayerInputComponent->BindAction(GrabActionName, IE_Pressed, this, &ASimulationCharacter::OnGrabPressed);
    PlayerInputComponent->BindAction(GrabActionName, IE_Released, this, &ASimulationCharacter::OnGrabReleased);
}

void ASimulationCharacter::Interact()
{
    if (InteractionComponent)
    {
        InteractionComponent->Interact();
    }
}

void ASimulationCharacter::Grab()
{
    if (GrabbedActor)
    {
        // Release current object
        GrabbedActor->SetOwner(nullptr);
        GrabbedActor = nullptr;
        GrabMesh->SetVisibility(false);
    }
    else
    {
        // Find object to grab
        TArray<AActor*> OverlappingActors;
        GrabCollision->GetOverlappingActors(OverlappingActors);
        
        for (AActor* Actor : OverlappingActors)
        {
            if (Actor && Actor != this)
            {
                GrabbedActor = Actor;
                GrabbedActor->SetOwner(this);
                GrabMesh->SetVisibility(true);
                break;
            }
        }
    }
}

void ASimulationCharacter::OnInteractPressed()
{
    Interact();
}

void ASimulationCharacter::OnGrabPressed()
{
    Grab();
}

void ASimulationCharacter::OnGrabReleased()
{
    if (GrabbedActor)
    {
        GrabbedActor->SetOwner(nullptr);
        GrabbedActor = nullptr;
        GrabMesh->SetVisibility(false);
    }
}